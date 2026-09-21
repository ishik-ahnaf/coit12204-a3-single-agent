from unittest.mock import Mock, patch
from app.agent import TaskAgent
from app.tools import lookup_task, summarise_tasks


class TestTools:
    def test_lookup_task_finds_existing(self):
        result = lookup_task.invoke({"query": "assignment"})
        assert "COIT12204 Assessment 3" in result

    def test_lookup_task_no_match(self):
        result = lookup_task.invoke({"query": "nonexistent_xyz"})
        assert "No task found" in result

    def test_summarise_tasks_basic(self):
        result = summarise_tasks.invoke({"task_list": "exam study, grocery shopping, assessment writeup"})
        assert "Total tasks: 3" in result

    def test_summarise_tasks_empty(self):
        result = summarise_tasks.invoke({"task_list": ""})
        assert "No tasks" in result


class TestTaskAgent:
    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_agent_initialisation(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        assert agent.llm is not None
        assert len(agent.tools) == 2
        assert agent.state.error_count == 0

    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_agent_run_updates_state(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        agent.executor = Mock()
        agent.executor.invoke.return_value = {"output": "Test output", "intermediate_steps": []}
        result = agent.run("test query")
        assert result["output"] == "Test output"
        assert agent.state.last_suggestion == "Test output"

    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_agent_run_handles_exception(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        agent.executor = Mock()
        agent.executor.invoke.side_effect = RuntimeError("LLM timeout")
        result = agent.run("test query")
        assert "error" in result
        assert agent.state.error_count == 1

    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_agent_run_tracks_tool_call(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        agent.executor = Mock()
        mock_step = Mock()
        mock_step.tool = "lookup_task"
        agent.executor.invoke.return_value = {
            "output": "Found it",
            "intermediate_steps": [(mock_step, "result")],
        }
        agent.run("find assignment")
        assert agent.state.last_tool_call == "lookup_task"

    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_agent_reset_state(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        agent.state.update(action="test", error="oops")
        agent.reset_state()
        assert agent.state.error_count == 0

    @patch("app.agent.ChatGoogleGenerativeAI")
    def test_multiple_errors_increment_count(self, mock_chat):
        mock_chat.return_value = Mock()
        agent = TaskAgent()
        agent.executor = Mock()
        agent.executor.invoke.side_effect = RuntimeError("Fail 1")
        agent.run("query 1")
        agent.executor.invoke.side_effect = RuntimeError("Fail 2")
        agent.run("query 2")
        assert agent.state.error_count == 2