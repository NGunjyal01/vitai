"""
Database queries module for VitaI.
Uses psycopg2 connection pool with pgvector support on Supabase PostgreSQL.
"""

import json
import uuid
import threading
from contextlib import contextmanager
from datetime import date, datetime, timedelta

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from pgvector.psycopg2 import register_vector

from config import DATABASE_URL

# ---------------------------------------------------------------------------
# Connection pool (lazy singleton)
# ---------------------------------------------------------------------------

_pool = None
_pool_lock = threading.Lock()


def get_pool() -> SimpleConnectionPool:
    """Return the lazily-initialised connection pool singleton."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=DATABASE_URL,
                )
    return _pool


@contextmanager
def get_conn():
    """Context manager: checkout a connection and return it on exit."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        register_vector(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row):
    """Convert a RealDictRow to a plain dict (or None)."""
    return dict(row) if row else None


def _rows_to_list(rows):
    """Convert a list of RealDictRow to a list of plain dicts."""
    return [dict(r) for r in rows] if rows else []


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def save_report(user_id: str, file_name: str, file_url: str = None,
                status: str = "processing") -> str:
    """Insert a new report row and return its id."""
    report_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reports (id, user_id, file_name, file_url, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (report_id, user_id, file_name, file_url, status),
            )
    return report_id


def update_report_status(report_id: str, status: str, error_message: str = None,
                         raw_text: str = None, report_type: str = None,
                         report_date=None, source_lab: str = None):
    """Update mutable fields on an existing report."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE reports
                SET status        = %s,
                    error_message = COALESCE(%s, error_message),
                    raw_text      = COALESCE(%s, raw_text),
                    report_type   = COALESCE(%s, report_type),
                    report_date   = COALESCE(%s, report_date),
                    source_lab    = COALESCE(%s, source_lab)
                WHERE id = %s
                """,
                (status, error_message, raw_text, report_type,
                 report_date, source_lab, report_id),
            )


def get_report(report_id: str):
    """Return a single report dict or None."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            row = cur.fetchone()
    return _row_to_dict(row)


def get_reports(user_id: str):
    """Return all reports for a user, newest first."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM reports WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# Health metrics
# ---------------------------------------------------------------------------

def save_health_metric(user_id: str, report_id: str, metric_dict: dict,
                       embedding) -> str:
    """Insert a parsed health metric and return its id."""
    metric_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO health_metrics
                    (id, user_id, report_id, parameter_name, parameter_key,
                     abbreviation, value, unit, normal_range_low,
                     normal_range_high, status, percent_of_range,
                     embedding, recorded_at)
                VALUES
                    (%s, %s, %s, %s, %s,
                     %s, %s, %s, %s,
                     %s, %s, %s,
                     %s::vector, %s)
                """,
                (
                    metric_id,
                    user_id,
                    report_id,
                    metric_dict.get("parameter_name"),
                    metric_dict.get("parameter_key"),
                    metric_dict.get("abbreviation"),
                    metric_dict.get("value"),
                    metric_dict.get("unit"),
                    metric_dict.get("normal_range_low"),
                    metric_dict.get("normal_range_high"),
                    metric_dict.get("status"),
                    metric_dict.get("percent_of_range"),
                    str(list(embedding)) if embedding is not None else None,
                    metric_dict.get("recorded_at"),
                ),
            )
    return metric_id


def get_report_metrics(report_id: str):
    """Return all health metrics linked to a report."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, user_id, report_id, parameter_name, parameter_key,
                       abbreviation, value, unit, normal_range_low,
                       normal_range_high, status, percent_of_range,
                       recorded_at, created_at
                FROM health_metrics
                WHERE report_id = %s
                ORDER BY parameter_name
                """,
                (report_id,),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# Manual health entries
# ---------------------------------------------------------------------------

def save_manual_entry(user_id: str, parameter_name: str, parameter_key: str,
                      value, unit: str, normal_range_low, normal_range_high,
                      status: str, embedding) -> str:
    """Insert a manually-entered health metric and return its id."""
    entry_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO manual_health_entries
                    (id, user_id, parameter_name, parameter_key, value, unit,
                     normal_range_low, normal_range_high, status, source,
                     embedding, recorded_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s,
                     %s::vector, NOW())
                """,
                (
                    entry_id,
                    user_id,
                    parameter_name,
                    parameter_key,
                    value,
                    unit,
                    normal_range_low,
                    normal_range_high,
                    status,
                    "manual",
                    str(list(embedding)) if embedding is not None else None,
                ),
            )
    return entry_id


# ---------------------------------------------------------------------------
# Aggregated metric queries
# ---------------------------------------------------------------------------

def get_all_metric_texts(user_id: str):
    """Return id + display_text for every metric (for BM25 retrieval)."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id,
                       parameter_name || ': ' || value || ' ' || unit
                           || ' (' || status || ')' AS display_text
                FROM health_metrics
                WHERE user_id = %s

                UNION ALL

                SELECT id,
                       parameter_name || ': ' || value || ' ' || unit
                           || ' (' || status || ')' AS display_text
                FROM manual_health_entries
                WHERE user_id = %s
                """,
                (user_id, user_id),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


def get_latest_metrics(user_id: str):
    """Return the most recent value per parameter_key across both tables."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (parameter_key)
                       id, parameter_name, parameter_key, value, unit,
                       normal_range_low, normal_range_high, status,
                       recorded_at
                FROM (
                    SELECT id, parameter_name, parameter_key, value, unit,
                           normal_range_low, normal_range_high, status,
                           recorded_at
                    FROM health_metrics
                    WHERE user_id = %s

                    UNION ALL

                    SELECT id, parameter_name, parameter_key, value, unit,
                           normal_range_low, normal_range_high, status,
                           recorded_at
                    FROM manual_health_entries
                    WHERE user_id = %s
                ) combined
                ORDER BY parameter_key, recorded_at DESC
                """,
                (user_id, user_id),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


def get_metrics_for_parameter(user_id: str, parameter_key: str):
    """Return a time-series of values for a single parameter_key."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, parameter_name, parameter_key, value, unit,
                       normal_range_low, normal_range_high, status,
                       recorded_at
                FROM (
                    SELECT id, parameter_name, parameter_key, value, unit,
                           normal_range_low, normal_range_high, status,
                           recorded_at
                    FROM health_metrics
                    WHERE user_id = %s AND parameter_key = %s

                    UNION ALL

                    SELECT id, parameter_name, parameter_key, value, unit,
                           normal_range_low, normal_range_high, status,
                           recorded_at
                    FROM manual_health_entries
                    WHERE user_id = %s AND parameter_key = %s
                ) combined
                ORDER BY recorded_at ASC
                """,
                (user_id, parameter_key, user_id, parameter_key),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

def get_user_profile(user_id: str):
    """Return the user profile dict or None."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM user_profiles WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
    return _row_to_dict(row)


def save_user_profile(user_id: str, profile_data: dict):
    """Upsert a user profile (INSERT ... ON CONFLICT UPDATE)."""
    fields = [
        "full_name", "age", "gender", "height_cm", "weight_kg",
        "diet_type", "health_goal", "known_conditions", "family_conditions",
        "activity_level", "sleep_hours", "stress_level", "training_type",
        "training_frequency", "training_experience", "supplements",
        "goal_phase", "onboarding_completed",
    ]
    # Build only the columns present in profile_data
    cols = [f for f in fields if f in profile_data]
    if not cols:
        return

    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols)
    values = [
        json.dumps(profile_data[c]) if isinstance(profile_data[c], (list, dict))
        and c not in ("known_conditions", "family_conditions", "supplements")
        else profile_data[c]
        for c in cols
    ]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO user_profiles (id, {col_names})
                VALUES (%s, {placeholders})
                ON CONFLICT (id) DO UPDATE
                SET {updates}
                """,
                [user_id] + values,
            )


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def save_insight(user_id: str, insight_text: str, insight_type: str,
                 severity: str = "info", metadata=None,
                 report_id: str = None) -> str:
    """Insert an insight and return its id."""
    insight_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO insights
                    (id, user_id, triggered_by_report_id, insight_text,
                     insight_type, severity, metadata, is_read)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
                """,
                (
                    insight_id,
                    user_id,
                    report_id,
                    insight_text,
                    insight_type,
                    severity,
                    json.dumps(metadata) if metadata is not None else None,
                ),
            )
    return insight_id


def get_insights(user_id: str, limit: int = 10):
    """Return latest insights for a user."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM insights
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

def save_plan(user_id: str, plan_data: dict, retest_date=None,
              report_id: str = None) -> str:
    """Deactivate existing active plans, then insert a new active plan."""
    plan_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Deactivate current active plans
            cur.execute(
                """
                UPDATE plans SET is_active = FALSE
                WHERE user_id = %s AND is_active = TRUE
                """,
                (user_id,),
            )
            cur.execute(
                """
                INSERT INTO plans
                    (id, user_id, triggered_by_report_id, plan_data,
                     retest_target_date, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                (
                    plan_id,
                    user_id,
                    report_id,
                    json.dumps(plan_data),
                    retest_date,
                ),
            )
    return plan_id


def get_active_plan(user_id: str):
    """Return the currently active plan dict or None."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM plans
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user_id,),
            )
            row = cur.fetchone()
    return _row_to_dict(row)


def complete_plan_item(user_id: str, plan_id: str, item_key: str) -> str:
    """Mark a plan item as completed and return the completion id."""
    completion_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO plan_completions (id, user_id, plan_id, item_key)
                VALUES (%s, %s, %s, %s)
                """,
                (completion_id, user_id, plan_id, item_key),
            )
    return completion_id


# ---------------------------------------------------------------------------
# Symptom logs
# ---------------------------------------------------------------------------

def save_symptom_log(user_id: str, energy: int, mood: str,
                     symptoms: list, notes: str = None):
    """Upsert today's symptom log for the user."""
    log_id = str(uuid.uuid4())
    today = date.today()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO symptom_logs
                    (id, user_id, logged_date, energy_level, mood,
                     symptoms, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, logged_date) DO UPDATE
                SET energy_level = EXCLUDED.energy_level,
                    mood         = EXCLUDED.mood,
                    symptoms     = EXCLUDED.symptoms,
                    notes        = EXCLUDED.notes
                """,
                (log_id, user_id, today, energy, mood, symptoms, notes),
            )


# ---------------------------------------------------------------------------
# Fitness logs
# ---------------------------------------------------------------------------

def save_fitness_log(user_id: str, data_dict: dict):
    """Upsert today's fitness log for the user."""
    log_id = str(uuid.uuid4())
    today = date.today()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO fitness_logs
                    (id, user_id, steps, workout_minutes, workout_type,
                     training_volume, training_intensity, calories_burned,
                     calorie_intake, protein_grams, sleep_hours,
                     sleep_quality, water_glasses, body_weight_kg,
                     body_fat_percentage, source, logged_date)
                VALUES
                    (%s, %s, %s, %s, %s,
                     %s, %s, %s,
                     %s, %s, %s,
                     %s, %s, %s,
                     %s, %s, %s)
                ON CONFLICT (user_id, logged_date) DO UPDATE
                SET steps              = COALESCE(EXCLUDED.steps, fitness_logs.steps),
                    workout_minutes    = COALESCE(EXCLUDED.workout_minutes, fitness_logs.workout_minutes),
                    workout_type       = COALESCE(EXCLUDED.workout_type, fitness_logs.workout_type),
                    training_volume    = COALESCE(EXCLUDED.training_volume, fitness_logs.training_volume),
                    training_intensity = COALESCE(EXCLUDED.training_intensity, fitness_logs.training_intensity),
                    calories_burned    = COALESCE(EXCLUDED.calories_burned, fitness_logs.calories_burned),
                    calorie_intake     = COALESCE(EXCLUDED.calorie_intake, fitness_logs.calorie_intake),
                    protein_grams      = COALESCE(EXCLUDED.protein_grams, fitness_logs.protein_grams),
                    sleep_hours        = COALESCE(EXCLUDED.sleep_hours, fitness_logs.sleep_hours),
                    sleep_quality      = COALESCE(EXCLUDED.sleep_quality, fitness_logs.sleep_quality),
                    water_glasses      = COALESCE(EXCLUDED.water_glasses, fitness_logs.water_glasses),
                    body_weight_kg     = COALESCE(EXCLUDED.body_weight_kg, fitness_logs.body_weight_kg),
                    body_fat_percentage = COALESCE(EXCLUDED.body_fat_percentage, fitness_logs.body_fat_percentage),
                    source             = COALESCE(EXCLUDED.source, fitness_logs.source)
                """,
                (
                    log_id,
                    user_id,
                    data_dict.get("steps"),
                    data_dict.get("workout_minutes"),
                    data_dict.get("workout_type"),
                    data_dict.get("training_volume"),
                    data_dict.get("training_intensity"),
                    data_dict.get("calories_burned"),
                    data_dict.get("calorie_intake"),
                    data_dict.get("protein_grams"),
                    data_dict.get("sleep_hours"),
                    data_dict.get("sleep_quality"),
                    data_dict.get("water_glasses"),
                    data_dict.get("body_weight_kg"),
                    data_dict.get("body_fat_percentage"),
                    data_dict.get("source"),
                    today,
                ),
            )


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

def get_chat_history(user_id: str, limit: int = 10):
    """Return recent chat messages (role + content), newest first."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT role, content
                FROM chat_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


def save_chat_message(user_id: str, role: str, content: str):
    """Append a chat message."""
    msg_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_history (id, user_id, role, content)
                VALUES (%s, %s, %s, %s)
                """,
                (msg_id, user_id, role, content),
            )


# ---------------------------------------------------------------------------
# Health scores
# ---------------------------------------------------------------------------

def save_health_score(user_id: str, score_data: dict):
    """Insert a health score snapshot."""
    score_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO health_scores
                    (id, user_id, total_score, base_score,
                     lifestyle_modifier, category_scores, score_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    score_id,
                    user_id,
                    score_data.get("total_score"),
                    score_data.get("base_score"),
                    score_data.get("lifestyle_modifier"),
                    json.dumps(score_data.get("category_scores")),
                    json.dumps(score_data.get("score_data")),
                ),
            )


def get_score_history(user_id: str, limit: int = 10):
    """Return recent health score snapshots."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM health_scores
                WHERE user_id = %s
                ORDER BY calculated_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# Agent traces
# ---------------------------------------------------------------------------

def save_agent_trace(user_id: str, agent_name: str, output_data: dict,
                     trace_id: str = None, latency_ms: int = None,
                     input_data: dict = None, error: str = None):
    """Log an agent execution trace."""
    row_id = str(uuid.uuid4())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_traces
                    (id, user_id, trace_id, agent_name, input_data,
                     output_data, latency_ms, error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row_id,
                    user_id,
                    trace_id or str(uuid.uuid4()),
                    agent_name,
                    json.dumps(input_data) if input_data is not None else None,
                    json.dumps(output_data) if output_data is not None else None,
                    latency_ms,
                    error,
                ),
            )


# ---------------------------------------------------------------------------
# Composite / context helpers
# ---------------------------------------------------------------------------

def get_user_context_summary(user_id: str) -> dict:
    """
    Build a compact context dict with profile info and latest key metrics.
    Used to prime the LLM with relevant user state.
    """
    profile = get_user_profile(user_id)
    latest = get_latest_metrics(user_id)

    key_params = {
        "hemoglobin", "hba1c", "tsh", "cholesterol", "total_cholesterol",
        "hdl", "ldl", "triglycerides", "vitamin_d", "vitamin_b12",
        "iron", "ferritin", "creatinine", "fasting_glucose",
    }

    key_metrics = {}
    for m in latest:
        pk = m.get("parameter_key", "")
        if pk in key_params:
            key_metrics[pk] = {
                "value": m["value"],
                "unit": m["unit"],
                "status": m["status"],
                "recorded_at": str(m["recorded_at"]) if m.get("recorded_at") else None,
            }

    summary = {
        "profile": None,
        "key_metrics": key_metrics,
    }

    if profile:
        summary["profile"] = {
            "full_name": profile.get("full_name"),
            "age": profile.get("age"),
            "gender": profile.get("gender"),
            "height_cm": profile.get("height_cm"),
            "weight_kg": profile.get("weight_kg"),
            "diet_type": profile.get("diet_type"),
            "health_goal": profile.get("health_goal"),
            "known_conditions": profile.get("known_conditions"),
            "activity_level": profile.get("activity_level"),
            "training_type": profile.get("training_type"),
            "goal_phase": profile.get("goal_phase"),
        }

    return summary


# ---------------------------------------------------------------------------
# pgvector semantic search
# ---------------------------------------------------------------------------

def pgvector_search(user_id: str, query_embedding, limit: int = 20):
    """
    Cosine-distance similarity search across health_metrics and
    manual_health_entries using pgvector's <=> operator.
    """
    embedding_str = str(list(query_embedding))
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, parameter_name, parameter_key, value, unit,
                       status, recorded_at,
                       embedding <=> %s::vector AS distance
                FROM (
                    SELECT id, parameter_name, parameter_key, value, unit,
                           status, recorded_at, embedding
                    FROM health_metrics
                    WHERE user_id = %s AND embedding IS NOT NULL

                    UNION ALL

                    SELECT id, parameter_name, parameter_key, value, unit,
                           status, recorded_at, embedding
                    FROM manual_health_entries
                    WHERE user_id = %s AND embedding IS NOT NULL
                ) combined
                ORDER BY distance ASC
                LIMIT %s
                """,
                (embedding_str, user_id, user_id, limit),
            )
            rows = cur.fetchall()
    return _rows_to_list(rows)


# ---------------------------------------------------------------------------
# Active users
# ---------------------------------------------------------------------------

def get_active_users(days: int = 30):
    """Return user_ids who have chat_history or reports in the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT user_id
                FROM (
                    SELECT user_id FROM chat_history
                    WHERE created_at >= %s

                    UNION

                    SELECT user_id FROM reports
                    WHERE created_at >= %s
                ) active
                """,
                (cutoff, cutoff),
            )
            rows = cur.fetchall()
    return [str(r["user_id"]) for r in rows]
