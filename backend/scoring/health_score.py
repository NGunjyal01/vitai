"""
VitaI Health Platform — Health Score Calculator

Computes a 0–100 health score from the user's latest blood-work metrics,
adjusted by lifestyle factors (activity level, sleep quality).
"""

from datetime import datetime
from decimal import Decimal

from db.queries import get_latest_metrics, save_health_score, get_user_profile
from services.parameter_registry import (
    get_score_weight,
    get_category,
    SCORE_CATEGORIES,
    PARAMETER_REGISTRY,
)


# ---------------------------------------------------------------------------
# Status → multiplier mapping
# ---------------------------------------------------------------------------

_STATUS_MULTIPLIERS: dict[str, float] = {
    "normal": 1.0,
    "borderline_low": 0.6,
    "borderline_high": 0.6,
    "low": 0.2,
    "high": 0.2,
}

# ---------------------------------------------------------------------------
# Activity-level modifiers (profile.activity_level → points)
# ---------------------------------------------------------------------------

_ACTIVITY_MODIFIERS: dict[str, float] = {
    "very_active": 2.0,
    "moderately_active": 1.0,
    "lightly_active": 0.0,
    "sedentary": -2.0,
}

# ---------------------------------------------------------------------------
# Sleep-hours modifiers (profile.sleep_hours → points)
# ---------------------------------------------------------------------------

_SLEEP_MODIFIERS: dict[str, float] = {
    "more_than_8": 3.0,
    "7_to_8": 3.0,
    "6_to_7": 1.0,
    "5_to_6": -1.0,
    "less_than_5": -3.0,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* into the closed interval [lo, hi]."""
    return max(lo, min(hi, value))


def _to_float(val):
    """Convert Decimal or any numeric to plain float for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return val


def _get_lifestyle_modifier(user_id: str, profile: dict) -> float:
    """
    Derive a lifestyle modifier in the range [-5, +5] from the user's
    profile data (activity level and sleep hours).
    """
    modifier = 0.0

    if profile:
        activity_level = (profile.get("activity_level") or "").lower().strip()
        modifier += _ACTIVITY_MODIFIERS.get(activity_level, 0.0)

        sleep_hours = (profile.get("sleep_hours") or "").lower().strip()
        modifier += _SLEEP_MODIFIERS.get(sleep_hours, 0.0)

    return _clamp(modifier, -5.0, 5.0)


# ---------------------------------------------------------------------------
# Main scorer
# ---------------------------------------------------------------------------


def calculate_health_score(user_id: str) -> dict:
    """
    Calculate and persist a comprehensive health score for *user_id*.

    Returns a dict with total_score, base_score, lifestyle_modifier, grade,
    category breakdowns, and metadata.
    """

    # 1. Fetch latest metrics & user profile
    metrics = get_latest_metrics(user_id) or []
    profile = get_user_profile(user_id) or {}

    # 2. Accumulate per-category earned / available scores
    #    category_key → {"earned": float, "available": float, "parameters": [...]}
    category_data: dict[str, dict] = {}
    for cat_key in SCORE_CATEGORIES:
        category_data[cat_key] = {
            "earned": 0.0,
            "available": 0.0,
            "parameters": [],
        }

    total_earned = 0.0
    total_available = 0.0

    for metric in metrics:
        param_key = metric.get("parameter_key")
        if not param_key or param_key not in PARAMETER_REGISTRY:
            continue

        weight = get_score_weight(param_key)
        category = get_category(param_key)

        if weight <= 0 or not category or category not in category_data:
            continue

        status = (metric.get("status") or "").lower().strip()
        multiplier = _STATUS_MULTIPLIERS.get(status, 0.0)
        earned = weight * multiplier

        # Global totals
        total_earned += earned
        total_available += weight

        # Per-category totals
        category_data[category]["earned"] += earned
        category_data[category]["available"] += weight
        category_data[category]["parameters"].append({
            "parameter_key": param_key,
            "parameter_name": metric.get("parameter_name", param_key),
            "value": _to_float(metric.get("value")),
            "unit": metric.get("unit"),
            "status": metric.get("status"),
            "normal_range_low": _to_float(metric.get("normal_range_low")),
            "normal_range_high": _to_float(metric.get("normal_range_high")),
            "recorded_at": str(metric.get("recorded_at", "")),
            "weight": weight,
            "earned": round(earned, 2),
            "multiplier": multiplier,
        })

    # 3. Base score (percentage)
    base_score = (total_earned / total_available * 100.0) if total_available > 0 else 0.0

    # 4. Lifestyle modifier
    lifestyle_modifier = _get_lifestyle_modifier(user_id, profile)

    # 5. Final score, clamped 0–100
    final_score = _clamp(base_score + lifestyle_modifier, 0.0, 100.0)

    # 6. Grade
    if final_score >= 80:
        grade = "green"
    elif final_score >= 60:
        grade = "amber"
    else:
        grade = "red"

    # 7. Build per-category score dict
    category_scores: dict[str, dict] = {}
    categories_assessed = 0

    for cat_key, cat_meta in SCORE_CATEGORIES.items():
        cd = category_data[cat_key]
        has_data = cd["available"] > 0

        if has_data:
            cat_score = round(cd["earned"] / cd["available"] * 100.0)
            categories_assessed += 1
        else:
            cat_score = None

        category_scores[cat_key] = {
            "label": cat_meta["label"],
            "color": cat_meta["color"],
            "score": cat_score,
            "assessed": has_data,
            "parameters": cd["parameters"],
        }

    # 8. Assemble result
    result = {
        "total_score": round(final_score),
        "base_score": round(base_score),
        "lifestyle_modifier": round(lifestyle_modifier, 1),
        "grade": grade,
        "categories_assessed": categories_assessed,
        "total_categories": len(SCORE_CATEGORIES),
        "category_scores": category_scores,
        "calculated_at": datetime.utcnow().isoformat(),
    }

    # 9. Persist
    save_health_score(user_id, result)

    return result