import os
import threading
from typing import Any, Dict, List

class ConversationMemory:
    """Thread-safe context memory for conversational analytics."""
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._history = {}  # maps dataset_id (str) -> list of turns (dicts)
        self._lock = threading.Lock()

    def add_turn(self, dataset_id: str, question: str, answer: str, query_plan: dict, insight: str) -> None:
        """Appends a turn to the history of a dataset, extracting filters and columns."""
        selected_filters = []
        referenced_columns = set()

        steps = query_plan.get("steps", [])
        if not steps and "operation" in query_plan:
            steps = [query_plan]

        for step in steps:
            op = step.get("operation")
            # Collect referenced columns
            if "column" in step:
                referenced_columns.add(step["column"])
            if "target" in step:
                referenced_columns.add(step["target"])
            if "group" in step:
                g = step["group"]
                if isinstance(g, list):
                    referenced_columns.update(g)
                elif isinstance(g, str):
                    referenced_columns.add(g)

            # Collect filters
            if op == "filter":
                selected_filters.append({
                    "column": step.get("column"),
                    "operator": step.get("operator"),
                    "value": step.get("value")
                })

        turn = {
            "question": question,
            "answer": answer,
            "query_plan": query_plan,
            "insight": insight,
            "selected_filters": selected_filters,
            "referenced_columns": list(referenced_columns)
        }

        with self._lock:
            if dataset_id not in self._history:
                self._history[dataset_id] = []
            self._history[dataset_id].append(turn)
            
            # Limit history to configured length
            if len(self._history[dataset_id]) > self.max_turns:
                self._history[dataset_id] = self._history[dataset_id][-self.max_turns:]

    def get_history(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Returns the conversation history for a given dataset ID."""
        with self._lock:
            return list(self._history.get(dataset_id, []))

    def clear_history(self, dataset_id: str) -> None:
        """Clears conversation history for a dataset ID."""
        with self._lock:
            self._history.pop(dataset_id, None)

# Configurable memory length
max_turns_env = os.environ.get("MEMORY_MAX_TURNS", "5")
try:
    max_turns = int(max_turns_env)
except ValueError:
    max_turns = 5

conversation_memory = ConversationMemory(max_turns=max_turns)
