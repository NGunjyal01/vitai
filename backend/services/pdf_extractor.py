import pdfplumber
import pytesseract
from PIL import Image

# Tell pytesseract exactly where Tesseract is
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_with_pdfplumber(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_with_ocr(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=200).original
            text += pytesseract.image_to_string(img) + "\n"
    return text

def extract_text(file_path: str) -> str:
    text = extract_with_pdfplumber(file_path)
    if len(text.strip()) < 50:
        print("Falling back to OCR...")
        text = extract_with_ocr(file_path)
    return text