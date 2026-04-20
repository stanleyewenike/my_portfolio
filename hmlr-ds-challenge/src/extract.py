"""
extract.py — OCR-based text extraction from scanned PDF documents.

Uses PyMuPDF to render pages as images, then Tesseract OCR to extract text.
Includes image preprocessing to improve OCR accuracy on aged/photocopied documents.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageFilter
import pytesseract
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def render_page_to_image(page: fitz.Page, dpi: int = 300) -> Image.Image:
    """
    Render a PDF page to a PIL Image at the specified DPI.
    
    Args:
        page: PyMuPDF page object
        dpi: Resolution for rendering. 300 DPI recommended for OCR.
    
    Returns:
        PIL Image in RGB mode
    """
    pixmap = page.get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy.
    
    Steps:
        1. Convert to grayscale — reduces noise from colour artifacts
        2. Apply slight sharpening — compensates for scan blur
    
    Note: We avoid aggressive thresholding here as it can destroy
    text on documents with varying background intensities (e.g., Page 1
    has a complex tabular layout with grey areas).
    """
    grey = image.convert("L")
    sharpened = grey.filter(ImageFilter.SHARPEN)
    return sharpened


def extract_text_from_page(page: fitz.Page, dpi: int = 300) -> str:
    """
    Extract text from a single PDF page using OCR.
    
    Args:
        page: PyMuPDF page object
        dpi: Resolution for rendering
    
    Returns:
        Extracted text as string
    """
    image = render_page_to_image(page, dpi=dpi)
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    return text.strip()


def extract_all_pages(pdf_path: str, dpi: int = 300) -> list[dict]:
    """
    Extract text from all pages of a PDF document.
    
    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for OCR rendering
    
    Returns:
        List of dicts with keys: page_number, text, char_count, word_count
    """
    doc = fitz.open(pdf_path)
    results = []
    
    for i, page in enumerate(doc):
        logger.info(f"Processing page {i + 1}/{len(doc)}...")
        text = extract_text_from_page(page, dpi=dpi)
        
        results.append({
            "page_number": i + 1,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
        })
        logger.info(f"  Page {i + 1}: {len(text)} chars, {len(text.split())} words")
    
    doc.close()
    return results


# Allow standalone testing
if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/anonymised_1.pdf"
    pages = extract_all_pages(pdf_path)
    for p in pages:
        print(f"\n{'='*60}")
        print(f"Page {p['page_number']} | {p['word_count']} words")
        print(f"{'='*60}")
        print(p["text"][:500])
