# Medical safety guardrails -- post-processing for AI responses
import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate the AI is making a medical diagnosis
DIAGNOSTIC_PATTERNS = [
    re.compile(r"\byou\s+have\s+\w+", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+diagnosed\s+with\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+suffering\s+from\b", re.IGNORECASE),
    re.compile(r"\bthis\s+confirms\s+(that\s+)?you\s+have\b", re.IGNORECASE),
    re.compile(r"\byour\s+diagnosis\s+is\b", re.IGNORECASE),
    re.compile(r"\byou\s+definitely\s+have\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+(?:clearly\s+)?(?:diabetic|anemic|hypertensive|hypoglycemic)\b", re.IGNORECASE),
    re.compile(r"\bi\s+(?:can\s+)?diagnose\s+you\s+with\b", re.IGNORECASE),
    re.compile(r"\btest(?:s)?\s+(?:confirm|prove|show)\s+(?:that\s+)?you\s+have\b", re.IGNORECASE),
]

# Patterns that indicate the AI is prescribing or altering medication
MEDICATION_PATTERNS = [
    re.compile(r"\bstop\s+taking\s+(?:your\s+)?\w+", re.IGNORECASE),
    re.compile(r"\bstart\s+taking\s+(?:the\s+)?(?:medication|medicine|drug)\b", re.IGNORECASE),
    re.compile(r"\btake\s+\d+\s*(?:mg|ml|pills?|tablets?|capsules?)\b", re.IGNORECASE),
    re.compile(r"\bincrease\s+(?:your\s+)?(?:dose|dosage)\b", re.IGNORECASE),
    re.compile(r"\bdecrease\s+(?:your\s+)?(?:dose|dosage)\b", re.IGNORECASE),
    re.compile(r"\bswitch\s+(?:from\s+)?\w+\s+to\s+\w+", re.IGNORECASE),
    re.compile(r"\bi\s+(?:would\s+)?prescribe\b", re.IGNORECASE),
    re.compile(r"\byou\s+(?:should|must|need\s+to)\s+take\s+\w+\s+(?:medication|medicine|drug)\b", re.IGNORECASE),
    re.compile(r"\bdiscontinue\s+(?:your\s+)?\w+", re.IGNORECASE),
]

DISCLAIMER = (
    "This is for informational purposes only "
    "-- always consult a doctor for medical decisions."
)

# Safe replacement phrases
_DIAGNOSTIC_REPLACEMENT = (
    "your results may suggest a potential concern that should be reviewed by a healthcare professional"
)
_MEDICATION_REPLACEMENT = (
    "please discuss any medication changes with your healthcare provider"
)


def sanitize_response(text: str) -> str:
    """Scan AI response for diagnostic/medication language and sanitize."""
    if not text:
        return text

    violations_found = False

    # Check and replace diagnostic patterns
    for pattern in DIAGNOSTIC_PATTERNS:
        if pattern.search(text):
            logger.warning("Diagnostic pattern matched: %s", pattern.pattern)
            text = pattern.sub(_DIAGNOSTIC_REPLACEMENT, text)
            violations_found = True

    # Check and replace medication patterns
    for pattern in MEDICATION_PATTERNS:
        if pattern.search(text):
            logger.warning("Medication pattern matched: %s", pattern.pattern)
            text = pattern.sub(_MEDICATION_REPLACEMENT, text)
            violations_found = True

    # Append disclaimer if any violation was detected
    if violations_found:
        text = text.rstrip()
        if not text.endswith(DISCLAIMER):
            text = f"{text}\n\n{DISCLAIMER}"

    return text
