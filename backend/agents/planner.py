"""
Planner Agent — routes user messages to the right tools and context.

Analyzes the user's message alongside their health context, then outputs
a structured JSON execution plan that downstream agents use to decide
which tools to invoke and what data to retrieve.
"""

import json
import logging
import time
import uuid

from services.ai_client import ai_generate
from utils.resilience import repair_json
from db.queries import save_agent_trace

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid values
# ---------------------------------------------------------------------------
VALID_INTENTS = {
    "explain", "compare", "trend", "plan",
    "research", "symptom", "score", "general",
}
VALID_RESPONSE_FORMATS = {
    "conversational", "structured_plan", "comparison", "brief",
}
MAX_PRIORITY_MARKERS = 10

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
PLANNER_SYSTEM_PROMPT = """You are the Planner Agent for VitaI, a health analytics platform.

Your job: analyze the user's message and their health context, then output a JSON execution plan. Output ONLY valid JSON — no markdown, no explanation.

JSON schema:
{
  "intent": "explain|compare|trend|plan|research|symptom|score|general",
  "needs_research_agent": false,
  "needs_trend_analysis": false,
  "needs_symptom_context": false,
  "needs_fitness_context": false,
  "priority_markers": ["hemoglobin", "tsh"],
  "retrieval_focus": "description of what to search for",
  "response_format": "conversational|structured_plan|comparison|brief",
  "reasoning": "why this plan was chosen"
}

Rules for choosing intent:
- "explain" — the user asks what a lab value means, what is normal, or wants interpretation of a specific parameter.
- "compare" — the user wants to compare values across different reports or time points side by side.
- "trend" — the user wants to track how a value has changed over time (e.g., "how has my iron been trending?").
- "plan" — the user requests an action plan, diet plan, supplement plan, or improvement strategy.
- "research" — the user asks a medical knowledge question that goes beyond their own data (e.g., "what causes high TSH?").
- "symptom" — the user describes symptoms or asks about symptom-marker relationships.
- "score" — the user asks about their health score, how it is calculated, or how to improve it.
- "general" — greetings, thanks, off-topic, or anything that does not fit the above categories.

Rules for boolean flags:
- needs_research_agent: true when the question requires medical knowledge beyond the user's own data (intents: research, explain with complex context, symptom).
- needs_trend_analysis: true when the question involves changes over time (intents: trend, compare).
- needs_symptom_context: true when the user mentions symptoms, feelings, energy, or mood.
- needs_fitness_context: true when the question involves exercise, workout, steps, training, or physical performance.

Rules for priority_markers:
- List parameter registry keys (snake_case) that are most relevant to the user's question.
- Maximum 10 markers.
- For symptom-based questions, include markers commonly associated with those symptoms. Examples:
  - tired/fatigue → hemoglobin, tsh, vitamin_b12, ferritin, iron, vitamin_d, fasting_glucose
  - weight gain → tsh, fasting_glucose, hba1c, cholesterol, triglycerides
  - hair loss → ferritin, iron, tsh, vitamin_d, vitamin_b12, zinc
  - joint pain → vitamin_d, uric_acid, crp, esr
  - brain fog → vitamin_b12, tsh, fasting_glucose, hemoglobin, iron

Rules for retrieval_focus:
- A short natural-language description of what data to search for in the vector store and metric history.

Rules for response_format:
- "conversational" — for explain, general, symptom questions
- "structured_plan" — for plan requests
- "comparison" — for compare and trend questions
- "brief" — for score questions, greetings, simple factual answers
"""

# ---------------------------------------------------------------------------
# Fallback plan
# ---------------------------------------------------------------------------
FALLBACK_PLAN = {
    "intent": "general",
    "needs_research_agent": False,
    "needs_trend_analysis": False,
    "needs_symptom_context": False,
    "needs_fitness_context": False,
    "priority_markers": [],
    "retrieval_focus": "",
    "response_format": "conversational",
    "reasoning": "Fallback — could not parse AI planner output.",
}


def _validate_plan(plan: dict) -> dict:
    """Validate and sanitize a parsed plan dict. Returns a clean copy."""
    validated = {}

    # intent
    intent = plan.get("intent", "general")
    validated["intent"] = intent if intent in VALID_INTENTS else "general"

    # boolean flags
    for key in ("needs_research_agent", "needs_trend_analysis",
                "needs_symptom_context", "needs_fitness_context"):
        val = plan.get(key, False)
        validated[key] = bool(val) if isinstance(val, (bool, int)) else False

    # priority_markers
    markers = plan.get("priority_markers", [])
    if isinstance(markers, list):
        # ensure each element is a string, cap at MAX
        validated["priority_markers"] = [
            str(m) for m in markers if isinstance(m, str)
        ][:MAX_PRIORITY_MARKERS]
    else:
        validated["priority_markers"] = []

    # retrieval_focus
    validated["retrieval_focus"] = str(plan.get("retrieval_focus", ""))

    # response_format
    fmt = plan.get("response_format", "conversational")
    validated["response_format"] = fmt if fmt in VALID_RESPONSE_FORMATS else "conversational"

    # reasoning
    validated["reasoning"] = str(plan.get("reasoning", ""))

    return validated


def _build_user_prompt(message: str, user_context: dict) -> str:
    """Build the user-facing prompt that includes the message and context summary."""
    parts = [f"User message: {message}"]

    profile = user_context.get("profile")
    if profile:
        profile_lines = []
        if profile.get("age"):
            profile_lines.append(f"Age: {profile['age']}")
        if profile.get("gender"):
            profile_lines.append(f"Gender: {profile['gender']}")
        if profile.get("diet_type"):
            profile_lines.append(f"Diet: {profile['diet_type']}")
        if profile.get("health_goal"):
            profile_lines.append(f"Health goal: {profile['health_goal']}")
        if profile.get("known_conditions"):
            profile_lines.append(f"Known conditions: {profile['known_conditions']}")
        if profile.get("activity_level"):
            profile_lines.append(f"Activity level: {profile['activity_level']}")
        if profile.get("training_type"):
            profile_lines.append(f"Training type: {profile['training_type']}")
        if profile.get("goal_phase"):
            profile_lines.append(f"Goal phase: {profile['goal_phase']}")
        if profile_lines:
            parts.append("User profile:\n" + "\n".join(profile_lines))

    key_metrics = user_context.get("key_metrics")
    if key_metrics:
        metric_lines = []
        for param_key, info in key_metrics.items():
            metric_lines.append(
                f"  {param_key}: {info['value']} {info['unit']} ({info['status']})"
            )
        if metric_lines:
            parts.append("Latest key metrics:\n" + "\n".join(metric_lines))

    return "\n\n".join(parts)


async def plan_query(message: str, user_context: dict) -> dict:
    """
    Analyze the user's message and health context, then return
    a structured execution plan dict for downstream agents.
    """
    trace_id = str(uuid.uuid4())
    start = time.time()

    try:
        prompt = _build_user_prompt(message, user_context)

        raw = await ai_generate(
            prompt=prompt,
            system=PLANNER_SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.2,
        )

        parsed = repair_json(raw)
        plan = _validate_plan(parsed)

    except Exception as exc:
        logger.warning("Planner failed (%s), returning fallback plan.", exc)
        plan = dict(FALLBACK_PLAN)
        plan["reasoning"] = f"Fallback due to error: {exc}"

    latency_ms = int((time.time() - start) * 1000)

    # Log trace (best-effort, don't let logging failures break the flow)
    try:
        save_agent_trace(
            user_id=user_context.get("user_id"),
            agent_name="planner",
            output_data=plan,
            trace_id=trace_id,
            latency_ms=latency_ms,
            input_data={"message": message},
        )
    except Exception as trace_exc:
        logger.warning("Failed to save planner trace: %s", trace_exc)

    logger.info(
        "Planner completed in %dms — intent=%s, markers=%s",
        latency_ms, plan.get("intent"), plan.get("priority_markers"),
    )

    return plan
