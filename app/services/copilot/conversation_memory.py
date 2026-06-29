import threading
from typing import List, Dict, Any

class CopilotConversationMemory:
    """
    Thread-safe context memory for the AI Copilot.
    Stores previous user prompts, generated pipelines, and feedback/corrections.
    Memory remains session-based.
    """
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._history: Dict[str, List[Dict[str, Any]]] = {}  # maps session_id -> list of turns
        self._lock = threading.Lock()

    def add_turn(
        self,
        session_id: str,
        question: str,
        answer: str,
        generated_pipeline: Dict[str, Any],
        user_feedback: str = None
    ) -> None:
        """Appends a conversation turn to the history for a given session ID."""
        turn = {
            "question": question,
            "answer": answer,
            "generated_pipeline": generated_pipeline,
            "user_feedback": user_feedback
        }
        with self._lock:
            if session_id not in self._history:
                self._history[session_id] = []
            self._history[session_id].append(turn)
            
            # Limit history length
            if len(self._history[session_id]) > self.max_turns:
                self._history[session_id] = self._history[session_id][-self.max_turns:]

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves history list for a session ID."""
        with self._lock:
            return list(self._history.get(session_id, []))

    def clear_history(self, session_id: str) -> None:
        """Clears memory for a session ID."""
        with self._lock:
            self._history.pop(session_id, None)

# Configurable global singleton instance
copilot_memory = CopilotConversationMemory()
