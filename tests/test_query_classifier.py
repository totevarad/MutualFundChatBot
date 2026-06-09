"""Tests for the query classifier (Phase 4)."""
import pytest
from src.core.query_classifier import classify_query

def test_classify_advisory():
    res = classify_query("Which mutual fund should I invest in?")
    assert res["category"] == "advisory"
    assert res["confidence"] > 0.5

def test_classify_performance():
    res = classify_query("Compare returns of HDFC Flexi Cap")
    assert res["category"] == "performance_comparison"
    assert res["confidence"] > 0.5

def test_classify_factual():
    res = classify_query("What is the expense ratio?")
    assert res["category"] == "factual"
    assert res["confidence"] > 0.5

def test_classify_out_of_scope():
    res = classify_query("What is the weather today in Delhi?")
    assert res["category"] == "out_of_scope"
