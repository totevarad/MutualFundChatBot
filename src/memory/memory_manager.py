"""
Memory Manager — Retrieve, store, and clear user memories via Mem0.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


from src.memory.mem0_client import get_memory_client

def get_user_context(user_id: str, query: str) -> list[str]:
    """Fetch relevant memories for the current query."""
    if not user_id:
        return []
        
    client = get_memory_client()
    if not client:
        return []
        
    try:
        results = client.search(query=query, user_id=user_id, limit=5)
        # mem0 returns a list of dicts, typically with a "memory" key
        memories = []
        for res in results:
            if isinstance(res, dict) and "memory" in res:
                memories.append(res["memory"])
            elif isinstance(res, str):
                memories.append(res)
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memory for {user_id}: {e}")
        return []


def store_interaction(user_id: str, query: str, response: str):
    """Store the Q&A interaction as a memory."""
    if not user_id:
        return
        
    client = get_memory_client()
    if not client:
        return
        
    try:
        # We store the interaction. Mem0 will auto-extract preferences/facts.
        # It's usually better to just pass the user message or interaction.
        interaction = f"User asked: {query}\nBot answered: {response}"
        client.add(interaction, user_id=user_id)
        logger.info(f"Stored interaction in memory for {user_id}")
    except Exception as e:
        logger.error(f"Error storing memory for {user_id}: {e}")


def clear_user_memory(user_id: str):
    """Delete all stored memories for a user."""
    if not user_id:
        return
        
    client = get_memory_client()
    if not client:
        return
        
    try:
        client.delete_all(user_id=user_id)
        logger.info(f"Cleared memory for {user_id}")
    except Exception as e:
        logger.error(f"Error clearing memory for {user_id}: {e}")
