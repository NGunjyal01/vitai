"""
Intake Agent — Parses uploaded blood test PDFs into structured, enriched data.

Takes extracted text from a PDF blood test report and uses AI to parse out all
lab parameters, then normalizes, classifies, and enriches each parameter using
the parameter registry.
"""

import logging
from typing import Optional

from services.ai_client import ai_generate
from services.parameter_registry import (
    normalize_parameter_name,
    get_normal_range,
    classify_status,
    build_embedding_text,
    PARAMETER_REGISTRY,
)
from utils.resilience import repair_json

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt for the AI extraction step
# ---------------------------------------------------------------------------

INTAKE_SYSTEM_PROMPT = """\
You are a clinical lab report parser. Your job is to extract ALL lab test \
parameters from the provided blood test report text and return them as \
structured JSON.

Return JSON with this EXACT structure (no extra keys, no markdown, no \
explanation — ONLY the JSON object):

{
  "report_type": "CBC / Lipid Panel / Thyroid / Comprehensive / etc.",
  "report_date": "YYYY-MM-DD or null if not found",
  "source_lab": "Laboratory name or null if not found",
  "parameters": [
    {
      "name": "parameter display name exactly as written in the report",
      "value": numeric_value_only,
      "unit": "unit string as written",
      "reference_range": "full reference range string as written in report, or null",
      "reference_low": numeric_lower_bound_or_null,
      "reference_high": numeric_upper_bound_or_null
    }
  ]
}

RULES:
1. The "value" field MUST be a number (int or float). Never put text in this \
field. If a value is non-numeric (e.g. "Positive", "Reactive", "Non-Reactive") \
skip that parameter entirely.
2. Extract EVERY numeric lab parameter you can find, even minor or uncommon ones.
3. Parse reference ranges when present. If the report shows "13.0 - 17.0", set \
reference_low to 13.0 and reference_high to 17.0. If only one bound is given, \
set the other to null.
4. Handle Indian lab report formats. Common Indian labs include Thyrocare, \
Dr Lal PathLabs, SRL Diagnostics, Metropolis Healthcare, Redcliffe Labs, \
Apollo Diagnostics, Vijaya Diagnostic Centre, and others. These reports may use \
formats like "Lakh/uL" for platelets or "million/uL" for RBC.
5. If the report contains multiple panels (CBC + Lipid + Thyroid etc.), set \
report_type to "Comprehensive" and include ALL parameters across all panels.
6. Preserve the original unit string from the report.
7. For "report_date", look for collection date, report date, or sample date. \
Convert to YYYY-MM-DD format.
8. For "source_lab", look for the laboratory or diagnostic center name.
9. Do NOT invent or hallucinate values. Only extract what is explicitly present \
in the report text.
10. If a parameter appears multiple times (e.g. retested), use the most recent \
value.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val) -> Optional[float]:
    """Convert a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _compute_percent_of_range(
    value: float, range_low: float, range_high: float
) -> int:
    """
    Compute where *value* falls within [range_low, range_high] as a percentage.

    0   = at the low boundary
    100 = at the high boundary
    Values below or above the range yield < 0 or > 100 respectively.
    """
    span = range_high - range_low
    if span == 0:
        return 100 if value >= range_high else 0
    return int(round(((value - range_low) / span) * 100))


def _abbreviation_for_key(key: str) -> Optional[str]:
    """Return a short abbreviation for a registry parameter key."""
    entry = PARAMETER_REGISTRY.get(key)
    if not entry:
        return None
    # Use the key itself as abbreviation if it is short (<=5 chars),
    # otherwise pick the shortest alias.
    if len(key) <= 5:
        return key.upper()
    aliases = entry.get("aliases", [])
    if aliases:
        shortest = min(aliases, key=len)
        if len(shortest) <= 8:
            return shortest.upper()
    return key.upper()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def parse_report(
    extracted_text: str, user_profile: dict = None
) -> dict:
    """
    Parse extracted PDF text into structured, enriched lab data.

    Parameters
    ----------
    extracted_text : str
        Raw text extracted from a blood test PDF.
    user_profile : dict, optional
        User profile with keys like ``sex``, ``goal``, ``training_frequency``,
        ``is_athlete`` — used to select gender/fitness-adjusted reference ranges.

    Returns
    -------
    dict
        {
            "report_type": str,
            "report_date": str | None,
            "source_lab": str | None,
            "parameters": [ ... enriched parameter dicts ... ]
        }
    """
    if not extracted_text or not extracted_text.strip():
        raise ValueError("No extracted text provided to intake agent.")

    # ----- Step 1: AI extraction -----
    # Truncate to ~24K chars to stay within Groq's context limit
    if len(extracted_text) > 24000:
        extracted_text = extracted_text[:24000]
        logger.warning("Intake agent: truncated text to 24000 chars for LLM context limit")

    logger.info("Intake agent: sending extracted text to AI for parsing (%d chars)", len(extracted_text))

    raw_response = await ai_generate(
        prompt=extracted_text,
        system=INTAKE_SYSTEM_PROMPT,
        json_mode=True,
        temperature=0.1,
    )

    # ----- Step 2: Parse & repair JSON -----
    parsed = repair_json(raw_response)

    report_type = parsed.get("report_type", "Unknown")
    report_date = parsed.get("report_date")
    source_lab = parsed.get("source_lab")
    raw_parameters = parsed.get("parameters", [])

    logger.info(
        "Intake agent: AI returned %d parameters (type=%s, lab=%s)",
        len(raw_parameters),
        report_type,
        source_lab,
    )

    # ----- Step 3: Enrich each parameter -----
    enriched_parameters: list[dict] = []

    for raw_param in raw_parameters:
        raw_name = raw_param.get("name", "")
        raw_value = _safe_float(raw_param.get("value"))

        # Skip parameters without a usable numeric value
        if raw_value is None:
            logger.debug("Skipping parameter '%s' — non-numeric value", raw_name)
            continue

        unit = raw_param.get("unit", "")
        ai_ref_range = raw_param.get("reference_range")
        ai_ref_low = _safe_float(raw_param.get("reference_low"))
        ai_ref_high = _safe_float(raw_param.get("reference_high"))

        # Try to match to the registry
        parameter_key = normalize_parameter_name(raw_name)
        matched = parameter_key is not None

        if matched:
            # --- Registry-matched parameter ---
            entry = PARAMETER_REGISTRY[parameter_key]
            display_name = entry["name"]
            abbreviation = _abbreviation_for_key(parameter_key)

            # Get gender/fitness-adjusted reference range
            ref_range = get_normal_range(parameter_key, user_profile)
            range_low = ref_range.get("low")
            range_high = ref_range.get("high")

            # Classify status
            if range_low is not None and range_high is not None:
                status = classify_status(raw_value, range_low, range_high)
                percent = _compute_percent_of_range(raw_value, range_low, range_high)
            else:
                status = "unknown"
                percent = 0

            # Build embedding text using registry-aware builder
            embedding_text = build_embedding_text(
                parameter_key, raw_value, unit, status
            )

        else:
            # --- Unmatched parameter (not in registry) ---
            display_name = raw_name
            abbreviation = None

            range_low = ai_ref_low
            range_high = ai_ref_high

            # Classify using AI-provided ranges if both are available
            if range_low is not None and range_high is not None:
                status = classify_status(raw_value, range_low, range_high)
                percent = _compute_percent_of_range(raw_value, range_low, range_high)
            else:
                status = "unknown"
                percent = 0

            # Build a plain embedding text (no registry context)
            status_label = status if status != "unknown" else "range unavailable"
            embedding_text = f"{raw_name}: {raw_value} {unit} ({status_label})"

        enriched_param = {
            "name": display_name,
            "parameter_key": parameter_key,
            "abbreviation": abbreviation,
            "value": raw_value,
            "unit": unit,
            "normal_range_low": range_low,
            "normal_range_high": range_high,
            "status": status,
            "percent_of_range": percent,
            "embedding_text": embedding_text,
            "matched": matched,
        }
        enriched_parameters.append(enriched_param)

    logger.info(
        "Intake agent: enriched %d parameters (%d matched, %d unmatched)",
        len(enriched_parameters),
        sum(1 for p in enriched_parameters if p["matched"]),
        sum(1 for p in enriched_parameters if not p["matched"]),
    )

    return {
        "report_type": report_type,
        "report_date": report_date,
        "source_lab": source_lab,
        "parameters": enriched_parameters,
    }