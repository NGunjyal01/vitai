# JSON repair and resilience utilities
import json
import re
import logging

logger = logging.getLogger(__name__)


def repair_json(raw_text: str) -> dict:
    """Parse JSON from AI response, handling markdown fences and malformed output."""

    text = raw_text.strip()

    # --- Step 1: Strip markdown code fences ---
    # Handles ```json ... ```, ``` ... ```, and variants with extra whitespace
    fence_pattern = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", re.DOTALL)
    match = fence_pattern.search(text)
    if match:
        text = match.group(1).strip()

    # --- Step 2: Try direct parse ---
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.debug("Direct JSON parse failed, attempting repairs")

    # --- Step 3: Extract first JSON object { ... } via brace matching ---
    first_brace = text.find("{")
    if first_brace != -1:
        depth = 0
        in_string = False
        escape_next = False
        end_idx = -1
        for i in range(first_brace, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        if end_idx != -1:
            candidate = text[first_brace : end_idx + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                text = candidate  # continue fixing this slice

    # --- Step 4: Fix common issues ---
    fixed = text

    # Remove trailing commas before } or ]
    fixed = re.sub(r",\s*([\]}])", r"\1", fixed)

    # Replace single quotes with double quotes (only outside existing double-quoted strings)
    # Simple heuristic: swap all single quotes to double quotes
    if "'" in fixed and '"' not in fixed:
        fixed = fixed.replace("'", '"')

    # Remove JS-style comments  // ... and /* ... */
    fixed = re.sub(r"//.*?$", "", fixed, flags=re.MULTILINE)
    fixed = re.sub(r"/\*.*?\*/", "", fixed, flags=re.DOTALL)

    # Strip control characters that break JSON
    fixed = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", fixed)

    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # --- Step 5: Last resort — eval-like parse with ast.literal_eval ---
    try:
        import ast

        result = ast.literal_eval(fixed)
        if isinstance(result, dict):
            return result
    except (ValueError, SyntaxError):
        pass

    raise ValueError(
        f"Could not parse JSON from AI response. "
        f"First 200 chars: {raw_text[:200]!r}"
    )
