from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os, uuid, shutil, json, tempfile
import time

load_dotenv()

app = FastAPI(title="VitaI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/reports")
async def upload_report(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    from db.queries import execute_query
    from tasks import process_report

    report_id = str(uuid.uuid4())
    suffix = os.path.splitext(file.filename)[1]
    tmp_path = os.path.join(tempfile.gettempdir(), f"{report_id}{suffix}")

    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    execute_query("""
        INSERT INTO reports (id, user_id, file_name, status)
        VALUES (%s, %s, %s, 'processing')
    """, (report_id, user_id, file.filename), fetch=False)

    process_report.delay(report_id, tmp_path, user_id)
    return {"report_id": report_id, "status": "processing"}

@app.get("/api/reports/{report_id}")
def get_report_status(report_id: str):
    from db.queries import execute_query
    rows = execute_query(
        "SELECT id, status, report_type, report_date, source_lab FROM reports WHERE id=%s",
        (report_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Report not found")
    return dict(rows[0])

@app.post("/api/chat")
async def chat(request: dict):
    from services.ai_client import stream_chat
    from services.embeddings import get_embedding
    from db.queries import execute_query

    user_id = request.get("user_id")
    message = request.get("message")

    if not user_id or not message:
        raise HTTPException(status_code=400, detail="user_id and message required")

    query_embedding = get_embedding(message)
    results = execute_query("""
        SELECT parameter_name, value, unit, status,
               normal_range_low, normal_range_high, recorded_at
        FROM health_metrics
        WHERE user_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT 10
    """, (user_id, str(query_embedding)))

    if results:
        context = "User's relevant health data:\n"
        for row in results:
            r = dict(row)
            context += (
                f"- {r['parameter_name']}: {r['value']} {r['unit'] or ''} "
                f"(status: {r['status']}, "
                f"normal range: {r['normal_range_low']}-{r['normal_range_high']})\n"
            )
    else:
        context = "No lab data available yet for this user."

    def generate():
        for chunk in stream_chat(context, message):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/score/{user_id}")
async def get_score(user_id: str):
    from db.queries import execute_query

    start = time.time()
    rows = execute_query("""
        SELECT hm.parameter_name, hm.value, hm.normal_range_low,
            hm.normal_range_high, hm.status
        FROM health_metrics hm
        JOIN (
            SELECT parameter_name, MAX(recorded_at) as max_time
            FROM health_metrics
            WHERE user_id = %s
            GROUP BY parameter_name
        ) latest
        ON hm.parameter_name = latest.parameter_name
        AND hm.recorded_at = latest.max_time
        WHERE hm.user_id = %s
    """, (user_id, user_id))
    print("DB TIME:", time.time() - start)
    if not rows:
        return {"score": None, "message": "No data yet — upload a report first"}

    WEIGHTS = {
        'HbA1c': 20, 'Fasting Glucose': 10,
        'Total Cholesterol': 10, 'LDL Cholesterol': 10, 'HDL Cholesterol': 5,
        'Hemoglobin': 10, 'TSH': 10,
        'Creatinine': 5, 'eGFR': 5,
        'Triglycerides': 5,
    }

    total_weight = 0
    weighted_score = 0

    for row in rows:
        r = dict(row)
        weight = WEIGHTS.get(r['parameter_name'], 2)
        if r['status'] == 'normal':
            points = weight
        elif r['status'] in ('borderline_low', 'borderline_high'):
            points = weight * 0.6
        else:
            points = weight * 0.2
        weighted_score += points
        total_weight += weight

    score = int((weighted_score / total_weight) * 100) if total_weight > 0 else 50
    score = max(0, min(100, score))
    return {"score": score, "parameters_analyzed": len(rows)}