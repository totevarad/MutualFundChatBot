"""Tests for the API (Phase 6)."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}

@patch("src.api.routes.query_pipeline")
def test_chat_endpoint(mock_pipeline):
    mock_pipeline.return_value = {
        "answer": "HDFC Flexi Cap has an expense ratio of 1.5%.",
        "source_url": "https://groww.in/hdfc-flexi-cap",
        "last_updated": "2024-01-01",
        "is_refusal": False
    }
    
    response = client.post(
        "/api/v1/chat",
        json={"query": "What is the expense ratio?", "user_id": "user123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "HDFC Flexi Cap has an expense ratio of 1.5%."
    assert data["is_refusal"] == False
    
    mock_pipeline.assert_called_once_with(query="What is the expense ratio?", user_id="user123")

@patch("src.api.routes.clear_user_memory")
def test_clear_memory_endpoint(mock_clear):
    response = client.delete("/api/v1/memory/user123")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    mock_clear.assert_called_once_with("user123")
