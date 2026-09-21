from app.state import AgentState


class TestAgentState:
    def test_initial_state(self):
        state = AgentState()
        assert state.last_suggestion is None
        assert state.error_count == 0
        assert state.action_history == []
        assert state.last_tool_call is None

    def test_update_with_suggestion(self):
        state = AgentState()
        state.update(action="test", suggestion="Do the assignment")
        assert state.last_suggestion == "Do the assignment"
        assert len(state.action_history) == 1

    def test_update_with_tool(self):
        state = AgentState()
        state.update(action="tool_call", tool_name="lookup_task")
        assert state.last_tool_call == "lookup_task"

    def test_error_count_increments(self):
        state = AgentState()
        state.update(action="run", error="Timeout")
        assert state.error_count == 1
        state.update(action="run", error="Rate limit")
        assert state.error_count == 2

    def test_error_count_not_incremented_on_success(self):
        state = AgentState()
        state.update(action="run", suggestion="Success")
        assert state.error_count == 0

    def test_action_history_accumulates(self):
        state = AgentState()
        state.update(action="first")
        state.update(action="second")
        state.update(action="third")
        assert len(state.action_history) == 3

    def test_to_dict_serialisation(self):
        state = AgentState()
        state.update(action="test", suggestion="Hello", tool_name="lookup_task")
        d = state.to_dict()
        assert d["last_suggestion"] == "Hello"
        assert d["last_tool_call"] == "lookup_task"
        assert d["action_count"] == 1

    def test_reset(self):
        state = AgentState()
        state.update(action="test", suggestion="Hello", error="Oops")
        state.reset()
        assert state.last_suggestion is None
        assert state.error_count == 0
        assert state.action_history == []

    def test_history_trimmed_in_snapshot(self):
        state = AgentState()
        for i in range(10):
            state.update(action=f"action_{i}")
        d = state.to_dict()
        assert d["action_count"] == 10
        assert len(d["recent_actions"]) == 5