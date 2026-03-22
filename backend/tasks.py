from celery_app import celery
from services.pdf_extractor import extract_text
from backend.services.gemini_ai_client import parse_lab_report
from services.embeddings import get_embedding
from db.queries import execute_query
from datetime import datetime

@celery.task
def process_report(report_id: str, file_path: str, user_id: str):
    print(f"\n--- Processing report {report_id} ---")
    try:
        text = extract_text(file_path)
        print(f"Extracted {len(text)} characters")

        parsed = parse_lab_report(text)
        params = parsed.get('parameters', [])
        print(f"Parsed {len(params)} parameters")

        report_date = parsed.get('report_date') or datetime.now().date().isoformat()
        execute_query("""
            UPDATE reports SET
                status = 'processed',
                raw_text = %s,
                report_type = %s,
                report_date = %s,
                source_lab = %s
            WHERE id = %s
        """, (text, parsed.get('report_type'), report_date,
              parsed.get('source_lab'), report_id), fetch=False)

        saved = 0
        for param in params:
            try:
                embed_text = f"{param['name']}: {param['value']} {param.get('unit','')} {param.get('status','')}"
                embedding = get_embedding(embed_text)
                execute_query("""
                    INSERT INTO health_metrics
                    (user_id, report_id, parameter_name, abbreviation,
                     value, unit, normal_range_low, normal_range_high,
                     status, percent_of_range, embedding, recorded_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector,%s)
                """, (
                    user_id, report_id,
                    param.get('name'), param.get('abbreviation'),
                    param.get('value'), param.get('unit'),
                    param.get('normal_range_low'), param.get('normal_range_high'),
                    param.get('status'), param.get('percent_of_range'),
                    str(embedding), report_date
                ), fetch=False)
                saved += 1
            except Exception as e:
                print(f"  Error saving {param.get('name')}: {e}")

        print(f"Saved {saved}/{len(params)} metrics")
        return {"status": "ok", "saved": saved}

    except Exception as e:
        print(f"Task failed: {e}")
        execute_query(
            "UPDATE reports SET status='failed' WHERE id=%s",
            (report_id,), fetch=False
        )
        raise