# Analysis Report — HMLR Data Science Challenge

## Exploratory Data Analysis

The input document contains 4 scanned pages of historical UK planning decision notices. All pages are embedded JPEG images with no digital text layer, requiring OCR as a preprocessing step. Page dimensions vary: Page 1 is landscape (1863×1313px) while Pages 2–4 are portrait (~726×1050px), reflecting different source document formats.

Tesseract OCR at 300 DPI with grayscale preprocessing yielded usable text across all pages (170–626 words per page), though quality varied — Page 1's complex tabular layout and Page 3's aged print produced more artifacts than the cleaner Pages 2 and 4.

Four distinct document categories were identified: **Local Land Charges Register** (tabular form with multiple entries), **Planning Permission Approval Notice** (structured decision from local authority), **Conditional Planning Permission Grant** (permission with conditions under the 1971 Act), and **Approval of Details Notice** (discharge of conditions). Application numbers follow two main formats: `P/YY/NNNN` (local authority prefix) and `NN/YY/NNNN` (district council prefix). Applicant names appear with formal titles (Mr/Mrs) or as corporate entities (Ltd).

## Approach

The pipeline uses an **NLP-first approach**: OCR → zero-shot text classification → regex + NER entity extraction. Zero-shot classification via `facebook/bart-large-mnli` was chosen because the small sample size precludes training a custom model, and it generalises to unseen document formats without retraining. A keyword-based fallback classifier is included for environments without GPU/transformer dependencies. Named entity extraction combines regex patterns (application numbers, titled names) with spaCy NER (`en_core_web_sm`) for broader person/organisation detection.

## Limitations

- **OCR quality** — Aged or photocopied documents (Pages 1, 3) produce artifacts that reduce both classification and extraction accuracy. "Mrs" was consistently OCR'd as "Mra" on Page 1.
- **Page 3 missing entities** — The applicant name and application number are stated to be "on the reverse", which is not included in the scan.
- **Small sample size** — Category definitions and regex patterns are derived from 4 pages; additional document formats (refusal notices, appeal decisions, enforcement notices) would require extending both the candidate labels and extraction patterns.
- **Date/application number ambiguity** — Formats like `13/07/1998` overlap with application numbers like `02/80/1609`; a heuristic date filter is applied but edge cases may persist.

## Alternative Methods

- **Vision approach (CNN):** A pre-trained document classification model (e.g., `microsoft/dit-base` or LayoutLMv3) could classify pages directly from images, bypassing OCR for classification. This would be more robust to OCR errors but less interpretable and would still require OCR for entity extraction.
- **Hybrid OCR + layout:** Tools like `docTR` or `PaddleOCR` provide word-level bounding boxes alongside text, enabling layout-aware classification that could distinguish tabular registers from letter-format notices based on spatial structure rather than text content alone.
- **Fine-tuned NER:** With a larger labelled dataset, a domain-specific NER model fine-tuned on planning document entities (application references, party names, addresses) would likely outperform the generic spaCy model and regex patterns.
