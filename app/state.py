"""AgentState class for tracking internal state across agent runs."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_state")


STATE_FILE = "agent_state.json"


@dataclass
class AgentState:
    last_suggestion: Optional[str] = None
    error_count: int = 0
    action_history: list = field(default_factory=list)
    last_tool_call: Optional[str] = None

    def update(self, action: str, tool_name: Optional[str] = None,
               suggestion: Optional[str] = None, error: Optional[str] = None):
        timestamp = datetime.now().isoformat()
        entry = {"timestamp": timestamp, "action": action, "tool": tool_name}

        if suggestion:
            self.last_suggestion = suggestion
            entry["suggestion_preview"] = suggestion[:100]

        if error:
            self.error_count += 1
            entry["error"] = error
            logger.warning(f"State updated with error: {error}")

        if tool_name:
            self.last_tool_call = tool_name

        self.action_history.append(entry)
        logger.info(f"State transition: action={action}, tool={tool_name}, errors={self.error_count}")

    def to_dict(self) -> dict:
        return {
            "last_suggestion": self.last_suggestion,
            "error_count": self.error_count,
            "action_count": len(self.action_history),
            "last_tool_call": self.last_tool_call,
            "recent_actions": self.action_history[-5:],
        }

    def reset(self):
        self.last_suggestion = None
        self.error_count = 0
        self.action_history = []
        self.last_tool_call = None
        logger.info("State reset to initial values")
        self.save()

    def save(self, path: str = STATE_FILE):
        """Persist state to a JSON file. Bonus extension."""
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"State saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load(self, path: str = STATE_FILE):
        """Load state from JSON file if it exists. Bonus extension."""
        if not os.path.exists(path):
            logger.info(f"No state file at {path}; starting fresh")
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self.last_suggestion = data.get("last_suggestion")
            self.error_count = data.get("error_count", 0)
            self.last_tool_call = data.get("last_tool_call")
            self.action_history = data.get("recent_actions", [])
            logger.info(f"State loaded from {path}: error_count={self.error_count}")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")