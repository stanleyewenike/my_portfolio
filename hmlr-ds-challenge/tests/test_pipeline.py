"""
test_pipeline.py — Basic tests for the document processing pipeline.

Run with: python -m pytest tests/ -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.entities import extract_application_numbers, extract_names_regex, _is_likely_date
from src.classify import classify_keyword


class TestApplicationNumberExtraction:
    """Tests for application number regex patterns."""
    
    def test_p_format(self):
        text = "Application Number: P/00/0759"
        result = extract_application_numbers(text)
        assert "P/00/0759" in result
    
    def test_council_format(self):
        text = "Application No. 02/80/1609."
        result = extract_application_numbers(text)
        assert "02/80/1609" in result
    
    def test_date_filtering(self):
        """Dates should not be extracted as application numbers."""
        text = "Date of Application: 17/07/2000"
        result = extract_application_numbers(text)
        assert "17/07/2000" not in result
    
    def test_multiple_numbers(self):
        text = "P/98/0964 references P/96/0900 dated 13.12.96."
        result = extract_application_numbers(text)
        assert "P/98/0964" in result
        assert "P/96/0900" in result


class TestDateFilter:
    """Tests for the date/application number disambiguation."""
    
    def test_date_detected(self):
        assert _is_likely_date("17/07/2000") is True
        assert _is_likely_date("13/07/1998") is True
    
    def test_app_number_not_date(self):
        assert _is_likely_date("02/80/1609") is False
        assert _is_likely_date("P/00/0759") is False


class TestNameExtraction:
    """Tests for applicant name extraction."""
    
    def test_mr_name(self):
        text = "approval granted to Mr M Dale\ndated 17/07/2000"
        result = extract_names_regex(text)
        names = [e["name"] for e in result]
        assert any("Dale" in n for n in names)
    
    def test_mrs_name(self):
        text = "applicant Mrs AM Stephens\nof 55 Cunnery Road"
        result = extract_names_regex(text)
        names = [e["name"] for e in result]
        assert any("Stephens" in n for n in names)
    
    def test_company_name(self):
        text = "approval granted to My First Company Ltd., dated"
        result = extract_names_regex(text)
        types = [e["type"] for e in result]
        assert "ORGANISATION" in types


class TestKeywordClassification:
    """Tests for keyword-based classification."""
    
    def test_planning_permission(self):
        text = "planning permission notice of approval hereby granted"
        result = classify_keyword(text)
        assert result["category"] == "Planning Permission Approval Notice"
    
    def test_conditional(self):
        text = "grant of conditional planning permission subject to conditions"
        result = classify_keyword(text)
        assert result["category"] == "Conditional Planning Permission Grant"
    
    def test_approval_of_details(self):
        text = "approval of details approval has been granted"
        result = classify_keyword(text)
        assert result["category"] == "Approval of Details Notice"
    
    def test_charges_register(self):
        text = "conditions imposed registrar planning charges part 3"
        result = classify_keyword(text)
        assert result["category"] == "Local Land Charges Register"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
