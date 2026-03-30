# PDF text extraction with OCR fallback
import pdfplumber
import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    """Extract text from PDF. Uses pdfplumber first, falls back to OCR."""
    text = ""

    # --- Stage 1: pdfplumber (native text layer) ---
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        logger.info(
            "pdfplumber extracted %d characters from %s", len(text.strip()), file_path
        )
    except Exception as exc:
        logger.warning("pdfplumber failed on %s: %s", file_path, exc)

    # --- Stage 2: OCR fallback if pdfplumber yielded very little ---
    if len(text.strip()) < 50:
        logger.info("Falling back to OCR for %s", file_path)
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Convert page to a PIL image for Tesseract
                    page_image = page.to_image(resolution=300)
                    img = page_image.original  # PIL.Image object
                    ocr_text = pytesseract.image_to_string(img)
                    text += ocr_text + "\n"
                    logger.debug("OCR page %d: %d chars", i + 1, len(ocr_text))
            logger.info(
                "OCR extracted %d characters from %s", len(text.strip()), file_path
            )
        except Exception as exc:
            logger.error("OCR failed on %s: %s", file_path, exc)

    # --- Stage 3: Validate we got something useful ---
    cleaned = text.strip()
    if len(cleaned) < 20:
        raise ValueError(
            f"Could not extract text from PDF ({file_path}): "
            f"only {len(cleaned)} characters recovered."
        )

    return cleaned
