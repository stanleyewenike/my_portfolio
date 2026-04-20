# HMLR Data Scientist Challenge

Document classification and entity extraction pipeline for scanned UK planning decision notice

## Overview

This pipeline processes scanned PDF documents through three stages:

1. **OCR Text Extraction** — Renders PDF pages as images and extracts text using Tesseract OCR
2. **Page Classification** — Categorises each page using zero-shot NLP classification (Hugging Face transformers) with a keyword-based fallback
3. **Entity Extraction** — Extracts application numbers (regex) and applicant names (spaCy NER + regex)

## Setup

### Prerequisites

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on PATH

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify installation
tesseract --version
```

### Install Dependencies

```bash
# Clone the repository
git clone <repo-url>
cd hmlr-ds-challenge

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install packages
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

## Usage

### Run the full pipeline

```bash
# Using zero-shot transformer classification (recommended)
python -m src.pipeline data/anonymised_1.pdf --method zero_shot

# Using keyword-based classification (faster, no GPU required)
python -m src.pipeline data/anonymised_1.pdf --method keyword

# Without spaCy (regex-only entity extraction)
python -m src.pipeline data/anonymised_1.pdf --method keyword --no-spacy
```

### Output

Results are saved to `output/results.json` with the following structure:

```json
{
  "document": "anonymised_1.pdf",
  "total_pages": 4,
  "pages": [
    {
      "page_number": 1,
      "classification": {
        "category": "Local Land Charges Register",
        "confidence": 0.95
      },
      "entities": {
        "application_numbers": ["02/80/1609", "02/81/1237"],
        "applicant_names": [
          {"name": "Mr. & Mrs. J.M Doe", "type": "PERSON"},
          {"name": "My First Company Ltd.", "type": "ORGANISATION"}
        ]
      }
    }
  ]
}
```

### Run individual modules

```bash
# Text extraction only
python -m src.extract data/anonymised_1.pdf

# Classification only
python -m src.classify data/anonymised_1.pdf keyword

# Entity extraction only
python -m src.entities data/anonymised_1.pdf
```

## Project Structure

```
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── analysis_report.md        # EDA, limitations, and alternative methods
├── data/
│   └── anonymised_1.pdf      # Input document
├── src/
│   ├── __init__.py
│   ├── extract.py            # OCR text extraction (PyMuPDF + Tesseract)
│   ├── classify.py           # Zero-shot classification + keyword fallback
│   ├── entities.py           # NER + regex entity extraction
│   └── pipeline.py           # Main orchestrator
├── output/
│   └── results.json          # Pipeline output
└── tests/
    └── test_pipeline.py      # Unit tests
```

## Approach

**Classification:** Zero-shot NLI via `facebook/bart-large-mnli` — selected because the small sample size precludes training a custom model, and the approach generalises to unseen document formats without retraining.

**Entity Extraction:** Dual-method approach combining regex patterns (for structured references like application numbers) with spaCy NER (for person and organisation names). The regex patterns are tuned to UK planning document conventions.

See `analysis_report.md` for detailed EDA, limitations, and alternative methods considered

## Author

Stanley Francis Ewenike
