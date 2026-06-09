"""Tests for guardrails — PII detection, input sanitization, output validation (Phase 4)."""
import pytest
from src.guardrails.input_sanitizer import sanitize_input
from src.guardrails.pii_detector import detect_pii
from src.guardrails.output_validator import validate_output

def test_sanitize_input():
    dirty = "   <script>alert(1)</script> Hello    World  \x00 "
    clean = sanitize_input(dirty)
    assert clean == "Hello World"

def test_detect_pii():
    text = "My PAN is ABCDE1234F and phone is 9876543210."
    res = detect_pii(text)
    types_found = [r["type"] for r in res]
    assert "pan" in types_found
    assert "phone" in types_found

def test_validate_output_valid():
    output = {"answer": "The expense ratio is 1.5%."}
    res = validate_output(output)
    assert res["is_valid"] == True
    assert res["has_advisory_language"] == False

def test_validate_output_advisory():
    output = {"answer": "I recommend you buy this fund immediately."}
    res = validate_output(output)
    assert res["is_valid"] == False
    assert res["has_advisory_language"] == True
    assert "factual information" in res["corrected_answer"]
