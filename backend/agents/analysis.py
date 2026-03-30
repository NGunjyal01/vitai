"""
Analysis Agent — runs after report upload to generate cross-report insights.

Examines newly uploaded metrics against historical data, detects trends
and correlations, then uses AI to produce actionable health insights.
"""

import json
import logging
import time
import uuid
from decimal import Decimal

from services.ai_client import ai_generate
from db.queries import (
    get_report_metrics,
    get_metrics_for_parameter,
    save_insight,
    get_user_profile,
    save_agent_trace,
)
from services.correlation_engine import detect_correlations
from utils.resilience import repair_json

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_float(val) -> float | None:
    """Safely convert a metric value to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _compute_trend(history: list[dict]) -> dict | None:
    """
    Given a time-ordered list of metric dicts (oldest first), compute
    the trend between the two most recent values.

    Returns a dict with: direction, previous_value, latest_value,
    percent_change, parameter_name, parameter_key, unit, status.
    Returns None if fewer than 2 numeric values exist.
    """
    # Filter to entries with numeric values
    numeric = []
    for entry in history:
        fval = _to_float(entry.get("value"))
        if fval is not None:
            numeric.append({**entry, "_fval": fval})

    if len(numeric) < 2:
        return None

    previous = numeric[-2]
    latest = numeric[-1]

    prev_val = previous["_fval"]
    lat_val = latest["_fval"]

    if prev_val == 0:
        pct_change = 0.0 if lat_val == 0 else 100.0
    else:
        pct_change = abs(lat_val - prev_val) / abs(prev_val) * 100.0

    # Determine if moving toward or away from normal range
    low = _to_float(latest.get("normal_range_low"))
    high = _to_float(latest.get("normal_range_high"))

    if low is not None and high is not None:
        midpoint = (low + high) / 2.0
        prev_distance = abs(prev_val - midpoint)
        lat_distance = abs(lat_val - midpoint)

        if pct_change < 5.0:
            direction = "stable"
        elif lat_distance < prev_distance:
            direction = "improving"
        else:
            direction = "worsening"
    else:
        # No normal range info — use raw change direction
        if pct_change < 5.0:
            direction = "stable"
        elif lat_val > prev_val:
            direction = "increasing"
        else:
            direction = "decreasing"

    return {
        "parameter_name": latest.get("parameter_name"),
        "parameter_key": latest.get("parameter_key"),
        "unit": latest.get("unit"),
        "status": latest.get("status"),
        "direction": direction,
        "previous_value": prev_val,
        "latest_value": lat_val,
        "percent_change": round(pct_change, 1),
        "data_points": len(numeric),
    }


def _build_analysis_prompt(
    trends: list[dict],
    correlations: list[dict],
    profile: dict | None,
) -> str:
    """Build the prompt for the AI insight-generation call."""
    parts = []

    # User profile context
    if profile:
        profile_lines = []
        for key in ("full_name", "age", "gender", "diet_type",
                     "health_goals", "known_conditions",
                     "activity_level", "training_type", "goal_phase"):
            val = profile.get(key)
            if val:
                profile_lines.append(f"  {key}: {val}")
        if profile_lines:
            parts.append("User profile:\n" + "\n".join(profile_lines))

    # Trending parameters
    if trends:
        trend_lines = []
        for t in trends:
            trend_lines.append(
                f"  {t['parameter_name']} ({t['parameter_key']}): "
                f"{t['previous_value']} -> {t['latest_value']} {t['unit']} "
                f"({t['direction']}, {t['percent_change']}% change, "
                f"status: {t['status']}, {t['data_points']} data points)"
            )
        parts.append("Trending parameters:\n" + "\n".join(trend_lines))
    else:
        parts.append("Trending parameters: None detected (first report or insufficient data).")

    # Correlations
    if correlations:
        corr_lines = []
        for c in correlations:
            corr_lines.append(f"  - {c.get('description', json.dumps(c))}")
        parts.append("Detected correlations:\n" + "\n".join(corr_lines))
    else:
        parts.append("Detected correlations: None.")

    parts.append(
        "Based on the above, generate 2 to 5 health insights as a JSON array. "
        "Each insight must have:\n"
        '  - "text": a clear, actionable insight sentence (1-3 sentences)\n'
        '  - "type": one of "trend", "correlation", "improvement", "alert"\n'
        '  - "severity": one of "info", "warning", "urgent"\n'
        '  - "metadata": {"related_parameters": ["param_key1", "param_key2"]}\n\n'
        "Rules:\n"
        '- Use "alert" type with "urgent" severity only for values that are dangerously '
        "out of range or worsening significantly.\n"
        '- Use "improvement" type when a value has moved toward normal.\n'
        '- Use "trend" type for notable trends (stable or changing).\n'
        '- Use "correlation" type when multiple markers suggest a connected issue.\n'
        "- Be specific: mention parameter names, values, and directions.\n"
        "- Be actionable: suggest what the user could do or discuss with their doctor.\n"
        "- Output ONLY the JSON array — no markdown, no wrapping text."
    )

    return "\n\n".join(parts)


ANALYSIS_SYSTEM_PROMPT = (
    "You are a medical health analyst AI for VitaI. You analyze blood work and health "
    "metrics to generate personalized insights. You are thorough but concise. "
    "Always output valid JSON — a JSON array of insight objects. No markdown fences."
)

VALID_INSIGHT_TYPES = {"trend", "correlation", "improvement", "alert"}
VALID_SEVERITIES = {"info", "warning", "urgent"}


def _validate_insights(raw_insights: list) -> list[dict]:
    """Validate and sanitize the list of insight dicts from AI output."""
    validated = []
    for item in raw_insights:
        if not isinstance(item, dict):
            continue

        text = item.get("text")
        if not text or not isinstance(text, str):
            continue

        itype = item.get("type", "trend")
        if itype not in VALID_INSIGHT_TYPES:
            itype = "trend"

        severity = item.get("severity", "info")
        if severity not in VALID_SEVERITIES:
            severity = "info"

        metadata = item.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Ensure related_parameters is a list of strings
        related = metadata.get("related_parameters", [])
        if not isinstance(related, list):
            related = []
        metadata["related_parameters"] = [str(p) for p in related]

        validated.append({
            "text": text.strip(),
            "type": itype,
            "severity": severity,
            "metadata": metadata,
        })

    # Cap at 5 insights
    return validated[:5]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run_analysis(user_id: str, report_id: str) -> list[dict]:
    """
    Run post-upload analysis for a report. Detects trends across historical
    data, runs the correlation engine, and generates AI-powered insights.

    Returns a list of saved insight dicts.
    """
    trace_id = str(uuid.uuid4())
    start = time.time()

    try:
        # 1. Fetch metrics from the new report
        report_metrics = get_report_metrics(report_id)
        if not report_metrics:
            logger.info("No metrics found for report %s, skipping analysis.", report_id)
            return []

        # 2. Fetch user profile
        profile = get_user_profile(user_id)

        # 3. For each metric, fetch historical values and detect trends
        trends = []
        metrics_dict = {}  # param_key -> latest value dict (for correlation engine)

        for metric in report_metrics:
            param_key = metric.get("parameter_key")
            if not param_key:
                continue

            # Build metrics_dict for correlation engine
            metrics_dict[param_key] = {
                "value": metric.get("value"),
                "unit": metric.get("unit"),
                "status": metric.get("status"),
                "normal_range_low": metric.get("normal_range_low"),
                "normal_range_high": metric.get("normal_range_high"),
            }

            # Fetch historical values for this parameter
            history = get_metrics_for_parameter(user_id, param_key)

            if len(history) >= 2:
                trend = _compute_trend(history)
                if trend is not None:
                    trends.append(trend)

        # 5. Run correlation engine
        correlations = []
        try:
            correlations = detect_correlations(metrics_dict, profile or {})
        except Exception as corr_exc:
            logger.warning(
                "Correlation engine failed for user %s: %s", user_id, corr_exc
            )

        # 6. Build AI prompt
        prompt = _build_analysis_prompt(trends, correlations, profile)

        # 7. Call AI to generate insights
        raw_response = await ai_generate(
            prompt=prompt,
            system=ANALYSIS_SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.4,
            max_tokens=2048,
        )

        # 8. Parse and validate
        parsed = repair_json(raw_response)

        # The response should be a list; if repair_json returned a dict
        # with an "insights" key, unwrap it
        if isinstance(parsed, dict):
            parsed = parsed.get("insights", parsed.get("data", [parsed]))
        if not isinstance(parsed, list):
            parsed = [parsed]

        insights = _validate_insights(parsed)

        if not insights:
            logger.warning(
                "AI returned no valid insights for report %s", report_id
            )

        # 9. Save each insight to the database
        saved_insights = []
        for insight in insights:
            try:
                insight_id = save_insight(
                    user_id=user_id,
                    insight_text=insight["text"],
                    insight_type=insight["type"],
                    severity=insight["severity"],
                    metadata=insight["metadata"],
                    report_id=report_id,
                )
                saved_insights.append({
                    "id": insight_id,
                    **insight,
                })
            except Exception as save_exc:
                logger.error(
                    "Failed to save insight for user %s: %s", user_id, save_exc
                )

        latency_ms = int((time.time() - start) * 1000)

        # 10. Log agent trace
        try:
            save_agent_trace(
                user_id=user_id,
                agent_name="analysis",
                output_data={
                    "report_id": report_id,
                    "trends_detected": len(trends),
                    "correlations_detected": len(correlations),
                    "insights_generated": len(saved_insights),
                    "insights": saved_insights,
                },
                trace_id=trace_id,
                latency_ms=latency_ms,
                input_data={
                    "report_id": report_id,
                    "metric_count": len(report_metrics),
                },
            )
        except Exception as trace_exc:
            logger.warning("Failed to save analysis trace: %s", trace_exc)

        logger.info(
            "Analysis completed for report %s in %dms — %d trends, %d correlations, %d insights",
            report_id, latency_ms, len(trends), len(correlations), len(saved_insights),
        )

        return saved_insights

    except Exception as exc:
        latency_ms = int((time.time() - start) * 1000)
        logger.error(
            "Analysis agent failed for report %s: %s", report_id, exc, exc_info=True
        )

        # Log error trace
        try:
            save_agent_trace(
                user_id=user_id,
                agent_name="analysis",
                output_data=None,
                trace_id=trace_id,
                latency_ms=latency_ms,
                input_data={"report_id": report_id},
                error=str(exc),
            )
        except Exception:
            pass

        return []
