"""
Rule-based correlation engine for VitaI.
Detects clinically meaningful patterns across multiple health metrics and
returns actionable insights.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: safely extract a numeric value from the metrics dict
# ---------------------------------------------------------------------------

def _val(metrics: dict, key: str) -> float | None:
    """Return the numeric value for *key* or None if missing / non-numeric."""
    entry = metrics.get(key)
    if entry is None:
        return None
    if isinstance(entry, dict):
        v = entry.get("value")
    else:
        v = entry
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _status(metrics: dict, key: str) -> str | None:
    """Return the status string for *key*, or None."""
    entry = metrics.get(key)
    if isinstance(entry, dict):
        return entry.get("status")
    return None


def _is_declining(metrics: dict, key: str) -> bool:
    """Heuristic: if the status is 'low' or 'borderline_low', treat as declining."""
    s = _status(metrics, key)
    return s in ("low", "borderline_low")


# ---------------------------------------------------------------------------
# Correlation rules
# ---------------------------------------------------------------------------

CORRELATION_RULES: list[dict] = [
    # 1. Metabolic syndrome pattern
    {
        "name": "metabolic_syndrome_pattern",
        "description": "Elevated HbA1c, high triglycerides, and low HDL suggest metabolic syndrome risk.",
        "check": lambda m, p: (
            (_val(m, "hba1c") is not None and _val(m, "hba1c") > 5.6)
            and (_val(m, "triglycerides") is not None and _val(m, "triglycerides") > 150)
            and (_val(m, "hdl") is not None and _val(m, "hdl") < 40)
        ),
        "severity": "warning",
        "insight_template": (
            "Pattern suggests metabolic syndrome risk. Your HbA1c ({hba1c}), "
            "triglycerides ({triglycerides}), and HDL ({hdl}) together indicate "
            "insulin resistance. Focus on reducing refined carbs, increasing "
            "fiber (dal, vegetables, oats), and adding 30 min of brisk walking daily. "
            "Consult your doctor for a fasting insulin test."
        ),
        "keys": ["hba1c", "triglycerides", "hdl"],
    },

    # 2. Iron deficiency cascade
    {
        "name": "iron_deficiency_cascade",
        "description": "Low ferritin stores with declining hemoglobin indicates iron deficiency progressing to anemia.",
        "check": lambda m, p: (
            (_val(m, "ferritin") is not None and _val(m, "ferritin") < 30)
            and (_is_declining(m, "hemoglobin") or (_val(m, "hemoglobin") is not None and _val(m, "hemoglobin") < 12))
        ),
        "severity": "warning",
        "insight_template": (
            "Your iron stores are low (ferritin: {ferritin}) and hemoglobin is affected "
            "({hemoglobin}). This is a classic iron deficiency cascade — your body has "
            "depleted its reserves and red blood cell production is dropping. Include "
            "iron-rich foods like ragi, jaggery, spinach, and pomegranate. Pair with "
            "vitamin C (lemon, amla) to boost absorption. Avoid tea/coffee with meals. "
            "See your doctor about iron supplementation if symptoms like fatigue or "
            "breathlessness persist."
        ),
        "keys": ["ferritin", "hemoglobin"],
    },

    # 3. Thyroid-metabolism link
    {
        "name": "thyroid_metabolism_link",
        "description": "Elevated TSH with high cholesterol may indicate subclinical hypothyroidism driving lipid changes.",
        "check": lambda m, p: (
            (_val(m, "tsh") is not None and _val(m, "tsh") > 4.0)
            and (_val(m, "total_cholesterol") is not None and _val(m, "total_cholesterol") > 200)
        ),
        "severity": "info",
        "insight_template": (
            "Elevated TSH ({tsh}) can cause cholesterol to rise ({total_cholesterol}). "
            "When the thyroid is underactive, the liver clears LDL cholesterol more slowly. "
            "Before starting statins, your doctor should evaluate thyroid treatment first — "
            "correcting TSH often normalises cholesterol on its own. Ensure adequate iodine "
            "(iodised salt) and selenium (Brazil nuts, eggs)."
        ),
        "keys": ["tsh", "total_cholesterol"],
    },

    # 4. Overtraining detection
    {
        "name": "overtraining_detection",
        "description": "High cortisol, low testosterone, and elevated CK suggest overtraining syndrome.",
        "check": lambda m, p: (
            (_val(m, "cortisol") is not None and _val(m, "cortisol") > 18)
            and (_val(m, "testosterone") is not None and _val(m, "testosterone") < 300)
            and (_val(m, "creatine_kinase") is not None and _val(m, "creatine_kinase") > 500)
        ),
        "severity": "warning",
        "insight_template": (
            "Elevated cortisol ({cortisol}) with low testosterone ({testosterone}) and "
            "high creatine kinase ({creatine_kinase}) suggests overtraining syndrome. "
            "Your body is under chronic stress and not recovering adequately. Consider: "
            "reduce training volume by 40-50% for 1-2 weeks, prioritise 7-8 hours of sleep, "
            "increase calorie intake (especially carbs around workouts), and add rest days. "
            "If symptoms persist (persistent fatigue, mood changes, poor performance), "
            "consult a sports medicine specialist."
        ),
        "keys": ["cortisol", "testosterone", "creatine_kinase"],
    },

    # 5. Creatine-kidney false alarm
    {
        "name": "creatine_kidney_false_alarm",
        "description": "Elevated creatinine with normal BUN in a creatine user is likely supplementation, not kidney disease.",
        "check": lambda m, p: (
            (_val(m, "creatinine") is not None and _val(m, "creatinine") > 1.3)
            and (_status(m, "bun") in ("normal", None) or (_val(m, "bun") is not None and _val(m, "bun") <= 20))
            and (
                isinstance(p, dict)
                and any(
                    "creatine" in (s or "").lower()
                    for s in (p.get("supplements") or [])
                )
            )
        ),
        "severity": "info",
        "insight_template": (
            "Elevated creatinine ({creatinine}) is likely from creatine supplementation, "
            "not kidney disease. Your BUN is normal, which is a reassuring sign. "
            "Creatine breaks down into creatinine, so supplementing 3-5g daily will "
            "raise serum creatinine by 0.1-0.3 mg/dL. If you want a cleaner kidney "
            "function marker, ask your doctor for a Cystatin C test, which is unaffected "
            "by creatine. Stay well hydrated (3-4L/day)."
        ),
        "keys": ["creatinine", "bun"],
    },

    # 6. B12 vegetarian risk
    {
        "name": "b12_vegetarian_risk",
        "description": "Low-normal B12 in a vegetarian diet suggests dietary insufficiency.",
        "check": lambda m, p: (
            (_val(m, "vitamin_b12") is not None and _val(m, "vitamin_b12") < 300)
            and (
                isinstance(p, dict)
                and (p.get("diet_type") or "").lower() in ("vegetarian", "vegan")
            )
        ),
        "severity": "info",
        "insight_template": (
            "Your B12 ({vitamin_b12} pg/mL) is on the lower side, which is common for "
            "vegetarians. B12 is almost exclusively found in animal products. Plant-based "
            "sources like fortified cereals and nutritional yeast help but are often "
            "insufficient. Consider a B12 supplement (methylcobalamin 1000-2000 mcg daily "
            "or weekly injections if very low). Include curd, paneer, and milk if "
            "lacto-vegetarian. Deficiency can cause fatigue, tingling, and cognitive issues."
        ),
        "keys": ["vitamin_b12"],
    },

    # 7. Vitamin D-thyroid link
    {
        "name": "vitamin_d_thyroid_link",
        "description": "Low vitamin D combined with borderline-high TSH — vitamin D deficiency can worsen thyroid function.",
        "check": lambda m, p: (
            (_val(m, "vitamin_d") is not None and _val(m, "vitamin_d") < 30)
            and (_val(m, "tsh") is not None and _val(m, "tsh") > 2.5)
        ),
        "severity": "info",
        "insight_template": (
            "Low vitamin D ({vitamin_d} ng/mL) can affect thyroid function (your TSH: "
            "{tsh}). Vitamin D plays a role in immune regulation and thyroid hormone "
            "production. Many Indians are deficient despite sunny weather due to indoor "
            "lifestyles and darker skin. Get 15-20 min of morning sun exposure, include "
            "fortified milk and eggs, and consider supplementing 60,000 IU weekly for "
            "8 weeks (under doctor supervision), then a maintenance dose."
        ),
        "keys": ["vitamin_d", "tsh"],
    },

    # 8. Sleep-glucose correlation
    {
        "name": "sleep_glucose_correlation",
        "description": "Short sleep duration is linked to elevated fasting glucose and insulin resistance.",
        "check": lambda m, p: (
            (_val(m, "fasting_glucose") is not None and _val(m, "fasting_glucose") > 100)
            and (
                isinstance(p, dict)
                and (p.get("sleep_hours") or "").lower() in ("less_than_5", "5_to_6")
            )
        ),
        "severity": "info",
        "insight_template": (
            "Poor sleep is strongly linked to elevated fasting glucose ({fasting_glucose} "
            "mg/dL). Research shows that sleeping less than 6 hours increases insulin "
            "resistance by up to 40%. Your reported sleep pattern ({sleep_hours}) may be "
            "a key driver. Prioritise: consistent sleep/wake times, no screens 1 hour "
            "before bed, cool dark room, and avoid heavy meals/caffeine after 4 PM. "
            "Improving sleep alone can reduce fasting glucose by 10-15 mg/dL."
        ),
        "keys": ["fasting_glucose"],
    },
]


# ---------------------------------------------------------------------------
# Detection engine
# ---------------------------------------------------------------------------

def detect_correlations(
    metrics: dict,
    user_profile: dict,
) -> list[dict]:
    """
    Check each correlation rule against the provided metrics and user profile.

    Parameters
    ----------
    metrics : dict
        Mapping of parameter_key -> {value, status, unit, ...}
    user_profile : dict
        User profile dict (diet_type, supplements, sleep_hours, etc.)

    Returns
    -------
    list[dict]
        Each matched correlation contains: name, description, severity,
        insight_text (the template rendered with actual values).
    """
    if not metrics:
        return []

    profile = user_profile or {}
    matched: list[dict] = []

    for rule in CORRELATION_RULES:
        try:
            if rule["check"](metrics, profile):
                # Build template values from the metric keys this rule uses
                template_values: dict[str, Any] = {}
                for key in rule.get("keys", []):
                    v = _val(metrics, key)
                    template_values[key] = v if v is not None else "N/A"

                # Add profile fields that templates might reference
                template_values["sleep_hours"] = profile.get("sleep_hours", "unknown")

                # Render the insight text
                try:
                    insight_text = rule["insight_template"].format(**template_values)
                except KeyError as e:
                    logger.warning(
                        "Template key missing for rule %s: %s", rule["name"], e
                    )
                    insight_text = rule["insight_template"]

                matched.append({
                    "name": rule["name"],
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "insight_text": insight_text,
                })
        except Exception:
            logger.exception("Error evaluating correlation rule %s", rule.get("name"))

    logger.info(
        "detect_correlations: checked %d rules, matched %d",
        len(CORRELATION_RULES),
        len(matched),
    )
    return matched
