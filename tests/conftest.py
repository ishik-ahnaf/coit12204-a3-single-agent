import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.state import AgentState
from app.agent import TaskAgent
from main import app


@pytest.fixture
def fresh_state():
    return AgentState()


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mocked_agent(monkeypatch):
    mock_agent = Mock(spec=TaskAgent)
    mock_agent.run.return_value = {
        "output": "Mocked agent response: due next Friday.",
        "intermediate_steps": [],
        "state_snapshot": {
            "last_suggestion": "Mocked agent response: due next Friday.",
            "error_count": 0,
            "action_count": 1,
            "last_tool_call": "lookup_task",
            "recent_actions": [],
        },
    }
    mock_agent.get_state.return_value = {
        "last_suggestion": None,
        "error_count": 0,
        "action_count": 0,
        "last_tool_call": None,
        "recent_actions": [],
    }
    mock_agent.reset_state.return_value = None

    import app.agent as agent_module
    monkeypatch.setattr(agent_module, "_agent_instance", mock_agent)
    return mock_agent