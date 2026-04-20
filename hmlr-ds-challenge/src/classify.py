"""
classify.py — Document page classification using NLP approaches.

Primary: Hugging Face zero-shot classification (facebook/bart-large-mnli)
Fallback: Keyword-based heuristic classification

The zero-shot approach is chosen because:
    1. Small sample size — training a custom model is impractical
    2. Off-the-shelf transformers demonstrate the essential skill
    3. Candidate labels can be adjusted without retraining
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Candidate labels derived from EDA of the sample documents.
# These represent the distinct planning document types observed.
CANDIDATE_LABELS = [
    "Local Land Charges Register",
    "Planning Permission Approval Notice",
    "Conditional Planning Permission Grant",
    "Approval of Details Notice",
]


def classify_zero_shot(
    text: str,
    candidate_labels: list[str] = CANDIDATE_LABELS,
    model_name: str = "facebook/bart-large-mnli",
) -> dict:
    """
    Classify a document page using Hugging Face zero-shot classification.
    
    Uses Natural Language Inference (NLI) to score how well the text
    matches each candidate label, without requiring task-specific training.
    
    Args:
        text: OCR-extracted text from the page
        candidate_labels: List of possible document categories
        model_name: Hugging Face model identifier
    
    Returns:
        Dict with keys: category, confidence, all_scores
    """
    from transformers import pipeline
    
    classifier = pipeline(
        "zero-shot-classification",
        model=model_name,
        device=-1,  # CPU — ensures portability
    )
    
    # Truncate text to avoid exceeding model's max token length (1024 for BART)
    # Use first ~2000 chars which typically contain the document header/title
    truncated = text[:2000]
    
    result = classifier(truncated, candidate_labels, multi_label=False)
    
    scores = {
        label: round(score, 4)
        for label, score in zip(result["labels"], result["scores"])
    }
    
    return {
        "category": result["labels"][0],
        "confidence": round(result["scores"][0], 4),
        "all_scores": scores,
    }


def classify_keyword(text: str) -> dict:
    """
    Keyword-based heuristic classification as a fallback method.
    
    This approach uses domain-specific phrases found during EDA to
    categorise documents. It is faster and more interpretable than
    the transformer approach, but less generalisable to unseen formats.
    
    Args:
        text: OCR-extracted text from the page
    
    Returns:
        Dict with keys: category, confidence, method
    """
    text_lower = text.lower()
    
    # Ordered by specificity — most specific patterns first.
    # Keywords tuned from EDA on OCR output, accounting for scan artifacts.
    rules = [
        {
            "category": "Approval of Details Notice",
            "keywords": ["approval of details", "approval has been granted"],
            "min_matches": 1,
        },
        {
            "category": "Local Land Charges Register",
            "keywords": [
                "planning charges", "land charges", "charges register",
                "registrar", "conditions imposed", "part 3", "part3",
            ],
            "min_matches": 2,  # Require 2+ matches to avoid false positives
        },
        {
            "category": "Conditional Planning Permission Grant",
            "keywords": ["conditional planning permission", "grant of conditional"],
            "anti_keywords": ["approval of details"],
            "min_matches": 1,
        },
        {
            "category": "Planning Permission Approval Notice",
            "keywords": [
                "planning permission", "notice of approval",
                "permission has been granted",
            ],
            "anti_keywords": [
                "conditional planning permission",
                "grant of conditional",
                "approval of details",
            ],
            "min_matches": 1,
        },
    ]
    
    for rule in rules:
        matches = sum(1 for kw in rule["keywords"] if kw in text_lower)
        anti_match = any(
            akw in text_lower for akw in rule.get("anti_keywords", [])
        )
        
        if matches >= rule["min_matches"] and not anti_match:
            return {
                "category": rule["category"],
                "confidence": min(0.5 + (matches * 0.15), 0.95),
                "method": "keyword_heuristic",
            }
    
    return {
        "category": "Unknown Document Type",
        "confidence": 0.0,
        "method": "keyword_heuristic",
    }


def classify_page(
    text: str,
    method: str = "zero_shot",
    candidate_labels: list[str] = CANDIDATE_LABELS,
) -> dict:
    """
    Classify a document page using the specified method.
    
    Args:
        text: OCR-extracted text
        method: 'zero_shot' for transformer, 'keyword' for heuristic
        candidate_labels: Labels for zero-shot classification
    
    Returns:
        Classification result dict
    """
    if method == "zero_shot":
        try:
            result = classify_zero_shot(text, candidate_labels)
            result["method"] = "zero_shot_nli"
            return result
        except Exception as e:
            logger.warning(f"Zero-shot failed ({e}), falling back to keyword method")
            return classify_keyword(text)
    else:
        return classify_keyword(text)


# Standalone testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.extract import extract_all_pages
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/anonymised_1.pdf"
    method = sys.argv[2] if len(sys.argv) > 2 else "keyword"
    
    pages = extract_all_pages(pdf_path)
    for page in pages:
        result = classify_page(page["text"], method=method)
        print(f"Page {page['page_number']}: {result['category']} "
              f"(confidence: {result['confidence']}, method: {result['method']})")
