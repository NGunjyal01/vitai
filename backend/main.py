import asyncio
import json
import os
import uuid
from datetime import datetime, timezone

import sentry_sdk
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import SENTRY_DSN
from db.queries import (
    save_report,
    update_report_status,
    get_report,
    get_reports,
    save_health_metric,
    get_report_metrics,
    get_user_profile,
    save_user_profile,
    get_latest_metrics,
    get_chat_history,
    save_chat_message,
    get_score_history,
    save_manual_entry,
    get_insights,
    save_insight,
    get_active_plan,
    get_plan_completions,
    complete_plan_item,
    save_symptom_log,
    get_symptom_logs,
    get_user_context_summary,
    save_agent_trace,
)
from services.pdf_extract import extract_text
from agents.intake import parse_report
from agents.planner import plan_query
from agents.analysis import run_analysis
from rag.embeddings import get_embedding
from rag.retrieval import hybrid_retrieve, compress_context
from scoring.health_score import calculate_health_score
from services.ai_client import ai_generate, ai_generate_stream
from services.medical_knowledge import get_medical_context
from services.parameter_registry import (
    normalize_parameter_name,
    get_normal_range,
    classify_status,
    build_embedding_text,
    PARAMETER_REGISTRY,
)
from utils.guardrails import sanitize_response
from utils.logging import setup_logging
from utils.rate_limit import limiter

# ---------------------------------------------------------------------------
# Sentry
# ---------------------------------------------------------------------------
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="VitaI", version="0.1.0")

# Logging
setup_logging()

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Coach system prompt
# ---------------------------------------------------------------------------
COACH_SYSTEM_PROMPT = (
    "You are VitaI, an empathetic and knowledgeable health coach. "
    "You help users understand their lab results and build healthier habits. "
    "Rules you MUST follow:\n"
    "- NEVER diagnose conditions or prescribe medication.\n"
    "- Always recommend consulting a healthcare professional for medical decisions.\n"
    "- Reference the user's actual lab values when discussing their health.\n"
    "- Be warm, supportive, and encouraging.\n"
    "- Provide actionable lifestyle suggestions (diet, exercise, sleep, stress management).\n"
    "- If a value is out of range, explain what it means in plain language and suggest "
    "evidence-based lifestyle changes.\n"
    "- Keep responses concise and easy to understand."
)

# ---------------------------------------------------------------------------
# Background task: process uploaded report
# ---------------------------------------------------------------------------

def process_report(report_id: str, user_id: str, file_path: str) -> None:
    """Run PDF extraction + AI parsing, then persist metrics."""
    try:
        # 1. Extract text from the uploaded file
        extracted_text = extract_text(file_path)

        # 2. Parse the report with the intake agent (async)
        user_profile = get_user_profile(user_id)
        result = asyncio.run(parse_report(extracted_text, user_profile))

        # 3. Save each parameter as a health metric with its embedding
        report_date = result.get("report_date")
        recorded_at = report_date if report_date else datetime.now(timezone.utc).isoformat()
        for param in result.get("parameters", []):
            embedding = get_embedding(param["embedding_text"])
            metric_dict = {
                "parameter_name": param["name"],
                "parameter_key": param.get("parameter_key"),
                "abbreviation": param.get("abbreviation"),
                "value": param["value"],
                "unit": param.get("unit", ""),
                "normal_range_low": param.get("normal_range_low"),
                "normal_range_high": param.get("normal_range_high"),
                "status": param.get("status"),
                "percent_of_range": param.get("percent_of_range"),
                "recorded_at": recorded_at,
            }
            save_health_metric(user_id, report_id, metric_dict, embedding)

        # 4. Mark report as processed
        update_report_status(
            report_id,
            "processed",
            report_type=result.get("report_type"),
            report_date=result.get("report_date"),
            source_lab=result.get("source_lab"),
            raw_text=extracted_text,
        )

        # 5. Run analysis agent for cross-report insights
        try:
            import asyncio as _asyncio
            _asyncio.run(run_analysis(user_id, report_id))
        except Exception:
            pass  # Don't fail report processing if analysis fails

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            update_report_status(report_id, "failed", error_message=str(e)[:500])
        except Exception:
            traceback.print_exc()
    finally:
        # 5. Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/reports", status_code=202)
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Query(...),
):
    # Save uploaded file to a temp location
    file_id = uuid.uuid4().hex
    file_path = f"/tmp/{file_id}_{file.filename}"
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Create report record in DB
    report_id = save_report(user_id, file.filename)

    # Kick off background processing
    background_tasks.add_task(process_report, report_id, user_id, file_path)

    return {"report_id": report_id, "status": "processing"}


@app.get("/api/reports")
async def list_reports(user_id: str = Query(...)):
    reports = get_reports(user_id)
    return reports


@app.get("/api/reports/{report_id}")
async def get_report_detail(report_id: str):
    report = get_report(report_id)
    if not report:
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    metrics = get_report_metrics(report_id)
    return {**report, "metrics": metrics}


@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a report and its associated health metrics."""
    from db.queries import get_conn
    import psycopg2.extras
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM health_metrics WHERE report_id = %s", (report_id,))
                cur.execute("DELETE FROM insights WHERE triggered_by_report_id = %s", (report_id,))
                cur.execute("DELETE FROM reports WHERE id = %s", (report_id,))
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/score")
async def get_health_score(user_id: str = Query(...)):
    score = calculate_health_score(user_id)
    return score


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body["message"]
    user_id = body["user_id"]

    # 1. Save user message to chat history
    save_chat_message(user_id, "user", message)

    # 2. Get user context summary (profile + key metrics)
    user_context = get_user_context_summary(user_id)
    user_profile = user_context.get("profile") or {}

    # 3. Planner agent — decides intent, priority markers, etc.
    plan = await plan_query(message, user_context)

    # 4. Hybrid RAG retrieve (semantic + keyword)
    records = hybrid_retrieve(user_id, message, plan, top_k=10)

    # 5. Compress retrieved records into a concise context string
    context_str = compress_context(records)

    # 6. Medical knowledge for priority markers
    medical_ctx = get_medical_context(
        plan.get("priority_markers", []), user_profile
    )

    # 7. Chat history (last 5 messages for conversational continuity)
    chat_history = get_chat_history(user_id, limit=5)
    history_lines = []
    for msg in reversed(chat_history):  # oldest first
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_lines.append(f"{role.upper()}: {content}")
    history_str = "\n".join(history_lines) if history_lines else "(no prior conversation)"

    # 8. Build full Coach prompt
    profile_summary = json.dumps(user_profile, default=str) if user_profile else "No profile data."
    full_prompt = (
        f"{COACH_SYSTEM_PROMPT}\n\n"
        f"### User Profile\n{profile_summary}\n\n"
        f"### Lab Results (RAG Context)\n{context_str}\n\n"
        f"### Medical Knowledge\n{medical_ctx}\n\n"
        f"### Recent Conversation\n{history_str}\n\n"
        f"### User Message\n{message}"
    )

    # 9-11. Stream response via SSE, apply guardrails, persist
    trace_start = asyncio.get_event_loop().time()

    async def event_generator():
        full_response = []
        async for chunk in ai_generate_stream(full_prompt):
            sanitized = sanitize_response(chunk)
            full_response.append(sanitized)
            yield f"data: {json.dumps({'text': sanitized})}\n\n"

        # After stream completes: save assistant response
        complete_text = "".join(full_response)
        save_chat_message(user_id, "assistant", complete_text)

        # Save agent trace for observability
        latency_ms = int((asyncio.get_event_loop().time() - trace_start) * 1000)
        try:
            save_agent_trace(
                user_id=user_id,
                agent_name="coach_chat",
                output_data={
                    "plan": plan,
                    "rag_records": len(records),
                    "response_length": len(complete_text),
                },
                latency_ms=latency_ms,
                input_data={"message": message},
            )
        except Exception:
            pass  # Don't fail the response if trace saving fails

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------

@app.post("/api/onboarding")
async def onboarding(request: Request):
    body = await request.json()
    user_id = body.pop("user_id", None)
    if not user_id:
        return JSONResponse(status_code=400, content={"error": "user_id is required"})

    # Map frontend field names to DB column names
    profile_data = {
        "full_name": body.get("full_name"),
        "age": body.get("age"),
        "gender": body.get("gender"),
        "height_cm": body.get("height_cm") or None,
        "weight_kg": body.get("weight_kg") or None,
        "diet_type": (body.get("diet_type") or "").lower().replace("-", "_").replace(" ", "_") or None,
        "health_goals": body.get("health_goals", [body.get("health_goal", "general_wellness")]),
        "known_conditions": body.get("conditions", body.get("known_conditions", [])),
        "family_conditions": body.get("family_history", body.get("family_conditions", [])),
        "activity_level": body.get("activity_level"),
        "sleep_hours": (body.get("sleep_hours") or "").replace("Less than 5", "less_than_5").replace("More than 8", "more_than_8").replace("5-6", "5_to_6").replace("6-7", "6_to_7").replace("7-8", "7_to_8") or None,
        "stress_level": body.get("stress_level"),
        "training_type": body.get("training_type") or None,
        "training_frequency": body.get("training_frequency") or None,
        "training_experience": body.get("training_experience") or None,
        "supplements": body.get("supplements", []),
        "goal_phase": (body.get("goal_phase") or "").lower() or None,
        "onboarding_completed": True,
    }
    # Remove None values so UPSERT doesn't overwrite with nulls
    profile_data = {k: v for k, v in profile_data.items() if v is not None}
    save_user_profile(user_id, profile_data)

    # Generate 3 WOW insights from the profile
    profile_summary = (
        f"Name: {body.get('full_name', 'N/A')}, "
        f"Age: {body.get('age', 'N/A')}, "
        f"Gender: {body.get('gender', 'N/A')}, "
        f"Height: {body.get('height_cm', 'N/A')} cm, "
        f"Weight: {body.get('weight_kg', 'N/A')} kg, "
        f"Diet: {body.get('diet_type', 'N/A')}, "
        f"Goal: {body.get('health_goal', 'N/A')}, "
        f"Conditions: {body.get('known_conditions', 'None')}, "
        f"Family history: {body.get('family_conditions', 'None')}, "
        f"Activity: {body.get('activity_level', 'N/A')}, "
        f"Sleep: {body.get('sleep_hours', 'N/A')}, "
        f"Stress: {body.get('stress_level', 'N/A')}"
    )

    insight_prompt = (
        f"Based on this user's health profile, generate exactly 3 surprising and motivating "
        f"health insights (WOW facts). Each insight should be personalized to their profile, "
        f"actionable, and encouraging. Return a JSON object with a single key 'insights' "
        f"containing an array of 3 strings.\n\n"
        f"User Profile:\n{profile_summary}"
    )

    insights = []
    try:
        raw = await ai_generate(insight_prompt, json_mode=True, max_tokens=1024, temperature=0.8)
        parsed = json.loads(raw)
        insight_list = parsed.get("insights", [])
        for text in insight_list[:3]:
            insight_id = save_insight(user_id, text, "onboarding", severity="info")
            insights.append({"id": insight_id, "text": text})
    except Exception:
        # If AI fails, continue without insights — profile is already saved
        pass

    return {"profile_saved": True, "insights": insights}


# ---------------------------------------------------------------------------
# Manual entry
# ---------------------------------------------------------------------------

@app.post("/api/manual-entry")
async def manual_entry(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    parameter_name = body.get("parameter_name")
    value = body.get("value")
    unit = body.get("unit", "")

    if not user_id or not parameter_name or value is None:
        return JSONResponse(
            status_code=400,
            content={"error": "user_id, parameter_name, and value are required"},
        )

    # Normalize the parameter name to a registry key
    param_key = normalize_parameter_name(parameter_name)

    # Get normal range and classify status
    user_profile = get_user_profile(user_id) or {}
    normal_range = {}
    status = "unknown"
    range_low = None
    range_high = None

    if param_key:
        normal_range = get_normal_range(param_key, user_profile)
        range_low = normal_range.get("low")
        range_high = normal_range.get("high")
        if range_low is not None and range_high is not None:
            try:
                status = classify_status(float(value), float(range_low), float(range_high))
            except (ValueError, TypeError):
                status = "unknown"

        # Use the registry unit if the caller didn't provide one
        if not unit:
            entry = PARAMETER_REGISTRY.get(param_key)
            if entry:
                unit = entry.get("unit", "")

    # Generate embedding
    embedding_text = build_embedding_text(
        param_key or parameter_name, value, unit, status
    )
    embedding = get_embedding(embedding_text)

    # Save
    entry_id = save_manual_entry(
        user_id=user_id,
        parameter_name=parameter_name,
        parameter_key=param_key or parameter_name,
        value=value,
        unit=unit,
        normal_range_low=range_low,
        normal_range_high=range_high,
        status=status,
        embedding=embedding,
    )

    # Recalculate health score
    try:
        calculate_health_score(user_id)
    except Exception:
        pass

    return {
        "id": entry_id,
        "parameter_name": parameter_name,
        "parameter_key": param_key or parameter_name,
        "value": value,
        "unit": unit,
        "normal_range_low": range_low,
        "normal_range_high": range_high,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@app.get("/api/insights")
async def list_insights(user_id: str = Query(...), limit: int = Query(10)):
    insights = get_insights(user_id, limit)
    return insights


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.get("/api/profile")
async def get_profile(user_id: str = Query(...)):
    profile = get_user_profile(user_id)
    if not profile:
        return JSONResponse(status_code=404, content={"error": "Profile not found"})
    return profile


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

@app.get("/api/plan")
async def get_plan(user_id: str = Query(...)):
    plan = get_active_plan(user_id)
    if not plan:
        return JSONResponse(status_code=404, content={"error": "No active plan found"})

    # Attach completions
    completions = get_plan_completions(user_id, plan["id"])
    plan["completions"] = completions

    # Parse plan_data if it's a string
    if isinstance(plan.get("plan_data"), str):
        try:
            plan["plan_data"] = json.loads(plan["plan_data"])
        except (json.JSONDecodeError, TypeError):
            pass

    return plan


@app.post("/api/plan/complete")
async def plan_complete(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    plan_id = body.get("plan_id")
    item_key = body.get("item_key")

    if not user_id or not plan_id or not item_key:
        return JSONResponse(
            status_code=400,
            content={"error": "user_id, plan_id, and item_key are required"},
        )

    completion_id = complete_plan_item(user_id, plan_id, item_key)
    return {"success": True, "completion_id": completion_id}


# ---------------------------------------------------------------------------
# Symptom log
# ---------------------------------------------------------------------------

@app.post("/api/symptom-log")
async def create_symptom_log(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    energy_level = body.get("energy_level", 0)
    mood = body.get("mood", "")
    symptoms = body.get("symptoms", [])
    notes = body.get("notes", "")

    if not user_id:
        return JSONResponse(status_code=400, content={"error": "user_id is required"})

    logged_date = body.get("logged_date")
    save_symptom_log(user_id, energy_level, str(mood), symptoms, notes, logged_date)
    return {"success": True}


@app.get("/api/symptom-log")
async def list_symptom_logs(user_id: str = Query(...), limit: int = Query(7)):
    logs = get_symptom_logs(user_id, limit)
    return logs


# ---------------------------------------------------------------------------
# Score history
# ---------------------------------------------------------------------------

@app.get("/api/score/history")
async def score_history(user_id: str = Query(...), limit: int = Query(10)):
    history = get_score_history(user_id, limit)
    return history