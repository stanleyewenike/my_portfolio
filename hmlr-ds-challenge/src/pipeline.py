"""
pipeline.py — Main orchestrator for the HMLR document processing pipeline.

Processes a PDF of scanned planning documents through three stages:
    1. OCR text extraction (extract.py)
    2. Page classification (classify.py)
    3. Entity extraction (entities.py)

Outputs structured JSON with per-page results.

Usage:
    python -m src.pipeline data/anonymised_1.pdf --method keyword
    python -m src.pipeline data/anonymised_1.pdf --method zero_shot
"""

import json
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extract import extract_all_pages
from src.classify import classify_page, CANDIDATE_LABELS
from src.entities import extract_entities

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def process_document(
    pdf_path: str,
    classification_method: str = "keyword",
    use_spacy: bool = True,
    output_path: str = "output/results.json",
) -> list[dict]:
    """
    Process a PDF document through the full pipeline.
    
    Args:
        pdf_path: Path to input PDF
        classification_method: 'zero_shot' or 'keyword'
        use_spacy: Whether to use spaCy NER (with regex fallback)
        output_path: Path for JSON output
    
    Returns:
        List of per-page result dicts
    """
    logger.info(f"Processing: {pdf_path}")
    logger.info(f"Classification method: {classification_method}")
    logger.info(f"NER method: {'spacy + regex' if use_spacy else 'regex only'}")
    
    # Stage 1: OCR text extraction
    logger.info("Stage 1/3: Extracting text via OCR...")
    pages = extract_all_pages(pdf_path)
    logger.info(f"  Extracted text from {len(pages)} pages")
    
    # Stage 2 & 3: Classify and extract entities per page
    results = []
    for page in pages:
        page_num = page["page_number"]
        text = page["text"]
        
        # Stage 2: Classification
        logger.info(f"Stage 2/3: Classifying page {page_num}...")
        classification = classify_page(
            text, method=classification_method
        )
        
        # Stage 3: Entity extraction
        logger.info(f"Stage 3/3: Extracting entities from page {page_num}...")
        entities = extract_entities(text, use_spacy=use_spacy)
        
        results.append({
            "page_number": page_num,
            "classification": {
                "category": classification["category"],
                "confidence": classification["confidence"],
                "method": classification["method"],
            },
            "entities": {
                "application_numbers": entities["application_numbers"],
                "applicant_names": [
                    {"name": e["name"], "type": e["type"]}
                    for e in entities["applicant_names"]
                ],
            },
            "metadata": {
                "ocr_word_count": page["word_count"],
                "ocr_char_count": page["char_count"],
            },
        })
    
    # Build output document
    output = {
        "document": Path(pdf_path).name,
        "processed_at": datetime.now().isoformat(),
        "total_pages": len(results),
        "configuration": {
            "classification_method": classification_method,
            "ner_method": "spacy + regex" if use_spacy else "regex_only",
            "ocr_engine": "tesseract",
            "ocr_dpi": 300,
        },
        "summary": {
            "categories_found": list(set(
                r["classification"]["category"] for r in results
            )),
            "total_application_numbers": sum(
                len(r["entities"]["application_numbers"]) for r in results
            ),
            "total_names_extracted": sum(
                len(r["entities"]["applicant_names"]) for r in results
            ),
        },
        "pages": results,
    }
    
    # Save output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"Results saved to {output_file}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PIPELINE RESULTS — {Path(pdf_path).name}")
    print(f"{'='*60}")
    for r in results:
        print(f"\nPage {r['page_number']}:")
        print(f"  Category:    {r['classification']['category']}")
        print(f"  Confidence:  {r['classification']['confidence']}")
        print(f"  App Numbers: {r['entities']['application_numbers'] or 'None found'}")
        names = [n['name'] for n in r['entities']['applicant_names']]
        print(f"  Names:       {names or 'None found'}")
    print(f"\n{'='*60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="HMLR Document Processing Pipeline"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to input PDF document",
    )
    parser.add_argument(
        "--method",
        choices=["zero_shot", "keyword"],
        default="keyword",
        help="Classification method (default: keyword)",
    )
    parser.add_argument(
        "--no-spacy",
        action="store_true",
        help="Disable spaCy NER, use regex only",
    )
    parser.add_argument(
        "--output",
        default="output/results.json",
        help="Output JSON path (default: output/results.json)",
    )
    
    args = parser.parse_args()
    
    process_document(
        pdf_path=args.pdf_path,
        classification_method=args.method,
        use_spacy=not args.no_spacy,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
