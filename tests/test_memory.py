"""Tests for the memory layer (Mem0) (Phase 5)."""
import pytest
from unittest.mock import patch, MagicMock
from src.memory.memory_manager import store_interaction, get_user_context, clear_user_memory

@patch("src.memory.memory_manager.get_memory_client")
def test_memory_flow(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Mock search to return a memory
    mock_client.search.return_value = [{"memory": "I like conservative funds."}]
    
    user_id = "test_user_123"
    
    # Store
    store_interaction(user_id, "I like conservative funds.", "Noted, you prefer conservative funds.")
    mock_client.add.assert_called_once()
    
    # Retrieve
    memories = get_user_context(user_id, "What should I invest in?")
    assert len(memories) == 1
    assert "conservative" in memories[0]
    
    # Clear
    clear_user_memory(user_id)
    mock_client.delete_all.assert_called_with(user_id=user_id)
