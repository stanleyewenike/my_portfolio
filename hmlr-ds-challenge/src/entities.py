"""
entities.py — Named Entity Recognition and pattern extraction.

Extracts two entity types from OCR text:
    1. Application numbers (regex patterns)
    2. Applicant names (spaCy NER + regex for title patterns)

Application numbers follow known formats in UK planning documents:
    - P/YY/NNNN (e.g., P/00/0759)
    - NN/YY/NNNN (e.g., 02/80/1609)
    - Variations with different separators

Applicant names are detected via:
    - Primary: spaCy Named Entity Recognition (PERSON entities)
    - Fallback: Regex matching title patterns (Mr, Mrs, Ms, Dr, etc.)
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Application Number Extraction
# ──────────────────────────────────────────────────────────────────────

# Regex patterns for UK planning application numbers.
# Ordered by specificity to avoid partial matches.
APPLICATION_NUMBER_PATTERNS = [
    # Format: P/YY/NNNN or P/YYYY/NNNN (with optional trailing letters)
    r"[(\[]*?(P/\d{2,4}/\d{3,5}[A-Z]?)",
    # Format: NN/YY/NNNN (council reference with district prefix)
    # Exclude dates: dates have middle values 01-12 and end values 1900-2099
    r"\b(\d{2}/\d{2}/\d{3,5})\b",
    # Format: Application No. followed by reference
    r"(?:Application\s+(?:No\.?|Number:?)\s*)([A-Z0-9/\-]+)",
]


def _is_likely_date(text: str) -> bool:
    """
    Heuristic to filter out dates that match application number patterns.
    Dates typically have format DD/MM/YYYY where DD <= 31 and MM <= 12.
    """
    parts = text.split("/")
    if len(parts) == 3:
        try:
            dd, mm, yyyy = int(parts[0]), int(parts[1]), int(parts[2])
            if dd <= 31 and mm <= 12 and 1900 <= yyyy <= 2099:
                return True
            # Also check MM/DD/YYYY
            if mm <= 31 and dd <= 12 and 1900 <= yyyy <= 2099:
                return True
        except ValueError:
            pass
    return False


def extract_application_numbers(text: str) -> list[str]:
    """
    Extract planning application numbers from OCR text.
    
    Uses regex patterns matching known UK planning reference formats.
    Deduplicates results while preserving order.
    
    Args:
        text: OCR-extracted text
    
    Returns:
        List of unique application numbers found
    """
    found = []
    
    for pattern in APPLICATION_NUMBER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    
    # Deduplicate, clean, and filter dates
    seen = set()
    unique = []
    for num in found:
        # Clean OCR artifacts: leading/trailing punctuation and brackets
        cleaned = num.strip(".,;: ()[]")
        # Minimum length filter: real app numbers are at least 5 chars
        if cleaned and len(cleaned) >= 5 and cleaned not in seen and not _is_likely_date(cleaned):
            seen.add(cleaned)
            unique.append(cleaned)
    
    return unique


# ──────────────────────────────────────────────────────────────────────
# Applicant Name Extraction
# ──────────────────────────────────────────────────────────────────────

# Regex for names preceded by common titles
# Handles: Mr, Mrs, Ms, Miss, Dr, and combinations like "Mr. & Mrs."
NAME_TITLE_PATTERN = re.compile(
    r"(?:Mr\.?|Mrs\.?|Ms\.?|Miss|Dr\.?)"       # Title
    r"(?:\s*(?:&|and)\s*"                        # Optional conjunction
    r"(?:Mr\.?|Mrs\.?|Ms\.?|Miss|Dr\.?))?"       # Optional second title
    r"\s+"                                        # Space before name
    r"([A-Z][A-Za-z.\-'\s]{1,40}?)"              # Name capture group
    r"(?=\s*(?:\n|,|dated|under|for|$))",         # Lookahead terminators
    re.MULTILINE,
)

# Pattern for company names (contains Ltd, Limited, PLC, etc.)
COMPANY_PATTERN = re.compile(
    r"(?:to\s+|granted\s+to\s+)"
    r"([A-Z][A-Za-z\s&.']+?"
    r"\s+(?:Ltd\.?|Limited|PLC|Inc\.?))",
    re.IGNORECASE,
)


def extract_names_regex(text: str) -> list[dict]:
    """
    Extract applicant names using regex patterns.
    
    Identifies names via title patterns (Mr/Mrs/Dr) and company
    names via corporate suffixes (Ltd/PLC).
    
    Args:
        text: OCR-extracted text
    
    Returns:
        List of dicts with keys: name, type (PERSON or ORGANISATION), method
    """
    entities = []
    seen = set()
    
    # Extract titled person names
    # Handles OCR variants: "Mrs" → "Mra", "Mr" → "Mr." etc.
    title_pattern = re.compile(
        r"((?:Mr[sa]?\.?|Mrs\.?|Ms\.?|Miss|Dr\.?)"
        r"(?:\s*(?:&|and)\s*(?:Mr[sa]?\.?|Mrs\.?|Ms\.?|Miss|Dr\.?))?)"
        r"\s+"
        r"([A-Z][A-Za-z.\-'\s]{1,40}?)"
        r"(?=\s*(?:\n|,|—|–|-\s|dated|under|for|of\s|$))",
        re.MULTILINE,
    )
    
    for match in title_pattern.finditer(text):
        title = match.group(1).strip()
        name_part = match.group(2).strip()
        full_name = f"{title} {name_part}"
        
        # Clean OCR artifacts
        full_name = re.sub(r"\s+", " ", full_name).strip()
        
        if full_name not in seen and len(name_part) > 1:
            seen.add(full_name)
            entities.append({
                "name": full_name,
                "type": "PERSON",
                "method": "regex_title_pattern",
            })
    
    # Extract company names
    for match in COMPANY_PATTERN.finditer(text):
        company = match.group(1).strip()
        company = re.sub(r"\s+", " ", company)
        if company not in seen:
            seen.add(company)
            entities.append({
                "name": company,
                "type": "ORGANISATION",
                "method": "regex_corporate_suffix",
            })
    
    return entities


def extract_names_spacy(text: str) -> list[dict]:
    """
    Extract applicant names using spaCy NER.
    
    Uses the en_core_web_sm model to identify PERSON and ORG entities.
    Filters for relevance by checking proximity to key phrases like
    'applicant', 'granted to', etc.
    
    Args:
        text: OCR-extracted text
    
    Returns:
        List of dicts with keys: name, type, method
    """
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except (ImportError, OSError) as e:
        logger.warning(f"spaCy not available ({e}), falling back to regex")
        return extract_names_regex(text)
    
    doc = nlp(text)
    entities = []
    seen = set()
    
    # Contextual phrases that indicate an entity is an applicant
    applicant_context = [
        "applicant", "granted to", "approval granted",
        "permission granted", "applied by",
    ]
    text_lower = text.lower()
    
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG"):
            name = ent.text.strip()
            # Skip very short or very long entities (likely OCR noise)
            if len(name) < 3 or len(name) > 60:
                continue
            if name not in seen:
                seen.add(name)
                entities.append({
                    "name": name,
                    "type": ent.label_,
                    "method": "spacy_ner",
                })
    
    return entities


def extract_entities(text: str, use_spacy: bool = True) -> dict:
    """
    Extract all entities from a document page.
    
    Args:
        text: OCR-extracted text
        use_spacy: Whether to attempt spaCy NER (falls back to regex)
    
    Returns:
        Dict with keys: application_numbers, applicant_names
    """
    app_numbers = extract_application_numbers(text)
    
    if use_spacy:
        names = extract_names_spacy(text)
    else:
        names = extract_names_regex(text)
    
    # If spaCy found nothing, supplement with regex
    if not names:
        names = extract_names_regex(text)
    
    return {
        "application_numbers": app_numbers,
        "applicant_names": names,
    }


# Standalone testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.extract import extract_all_pages
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/anonymised_1.pdf"
    pages = extract_all_pages(pdf_path)
    
    for page in pages:
        entities = extract_entities(page["text"], use_spacy=False)
        print(f"\nPage {page['page_number']}:")
        print(f"  Application numbers: {entities['application_numbers']}")
        print(f"  Names: {[e['name'] for e in entities['applicant_names']]}")
