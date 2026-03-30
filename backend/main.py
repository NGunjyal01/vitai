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
    get_latest_metrics,
    get_chat_history,
    save_chat_message,
    get_score_history,
)
from services.pdf_extract import extract_text
from agents.intake import parse_report
from rag.embeddings import get_embedding
from scoring.health_score import calculate_health_score
from services.ai_client import ai_generate_stream
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
    except Exception as e:
        update_report_status(report_id, "failed", error_message=str(e))
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


@app.get("/api/score")
async def get_health_score(user_id: str = Query(...)):
    score = calculate_health_score(user_id)
    return score


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body["message"]
    user_id = body["user_id"]

    # Gather context
    user_profile = get_user_profile(user_id)
    latest_metrics = get_latest_metrics(user_id)

    # Build context string from metrics
    context_lines = []
    for m in latest_metrics:
        line = (
            f"- {m.get('parameter_name', 'N/A')}: {m.get('value', 'N/A')} {m.get('unit', '')} "
            f"(ref: {m.get('normal_range_low', '?')}-{m.get('normal_range_high', '?')}, "
            f"status: {m.get('status', 'unknown')})"
        )
        context_lines.append(line)
    context_str = "\n".join(context_lines) if context_lines else "No lab data available yet."

    # Build full prompt
    full_prompt = (
        f"{COACH_SYSTEM_PROMPT}\n\n"
        f"### User Profile\n{json.dumps(user_profile, default=str) if user_profile else 'No profile data.'}\n\n"
        f"### Latest Lab Results\n{context_str}\n\n"
        f"### User Message\n{message}"
    )

    # Save user message to chat history
    save_chat_message(user_id, "user", message)

    # Stream the response via SSE
    async def event_generator():
        full_response = []
        async for chunk in ai_generate_stream(full_prompt):
            sanitized = sanitize_response(chunk)
            full_response.append(sanitized)
            yield f"data: {json.dumps({'text': sanitized})}\n\n"

        # After streaming completes, persist the assistant response
        complete_text = "".join(full_response)
        save_chat_message(user_id, "assistant", complete_text)

    return StreamingResponse(event_generator(), media_type="text/event-stream")