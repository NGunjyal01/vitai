import google.generativeai as genai
import json, re, os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

INTAKE_SYSTEM_PROMPT = """You are a medical data extraction system. Extract all lab parameters from the report text.
Return ONLY valid JSON, no other text, no markdown fences.
{
  "report_type": "CBC|Lipid Panel|Thyroid|Diabetes|Kidney|Liver|Other",
  "report_date": "YYYY-MM-DD or null",
  "source_lab": "lab name or null",
  "parameters": [
    {
      "name": "Full parameter name",
      "abbreviation": "abbreviation or null",
      "value": 0.0,
      "unit": "unit string",
      "normal_range_low": 0.0,
      "normal_range_high": 0.0,
      "status": "normal|low|high|borderline_low|borderline_high",
      "percent_of_range": 75
    }
  ]
}"""

COACH_SYSTEM_PROMPT = """You are an AI health coach with access to a user's lab results.
Explain health data in plain English and give actionable advice.
Rules:
- Never diagnose. Say "your values suggest" not "you have".
- Always reference specific values from the context.
- Be warm and encouraging, not clinical.
- If data is missing, say so clearly."""

def repair_json(raw: str) -> dict:
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from response: {raw[:300]}")

def parse_lab_report(text: str) -> dict:
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=INTAKE_SYSTEM_PROMPT
    )
    response = model.generate_content(
        f"Extract all lab parameters from this report:\n\n{text}"
    )
    raw = response.text
    print("Gemini raw response preview:", raw[:300])
    return repair_json(raw)

def stream_chat(context: str, message: str):
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=COACH_SYSTEM_PROMPT
    )
    response = model.generate_content(
        f"{context}\n\nUser question: {message}",
        stream=True
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text