"""LangChain-based single agent with state management and error handling."""

from dotenv import load_dotenv
load_dotenv()

import logging
from typing import Optional

from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import ALL_TOOLS
from app.prompts import ACTIVE_PROMPT
from app.state import AgentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")


class TaskAgent:
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        if llm is None:
            llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.2)

        self.llm = llm
        self.tools = ALL_TOOLS
        self.state = AgentState()
        self.state.load()  # Restore state from disk if available

        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=ACTIVE_PROMPT,
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        logger.info("TaskAgent initialised with %d tools", len(self.tools))

    def run(self, user_input: str) -> dict:
        logger.info("Agent run started: input='%s'", user_input[:80])
        try:
            result = self.executor.invoke({"input": user_input})

            tool_calls = []
            for step in result.get("intermediate_steps", []):
                if len(step) >= 2 and hasattr(step[0], "tool"):
                    tool_name = step[0].tool
                    if not tool_name.startswith("_"):
                        tool_calls.append(tool_name)

            last_tool = tool_calls[-1] if tool_calls else None

            self.state.update(
                action="agent_run_complete",
                tool_name=last_tool,
                suggestion=result.get("output", ""),
            )
            self.state.save()  # Persist after successful run

            logger.info("Agent run completed. Output length: %d, tools used: %s",
                        len(result.get("output", "")), tool_calls)

            return {
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "state_snapshot": self.state.to_dict(),
            }

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error("Agent run failed: %s", error_msg)

            self.state.update(action="agent_run_failed", error=error_msg)
            self.state.save()  # Persist after failed run too

            return {
                "output": "I encountered an error while processing your request. Please try rephrasing or try again later.",
                "intermediate_steps": [],
                "state_snapshot": self.state.to_dict(),
                "error": error_msg,
            }

    def reset_state(self):
        self.state.reset()
        logger.info("Agent state reset")

    def get_state(self) -> dict:
        return self.state.to_dict()


_agent_instance: Optional[TaskAgent] = None


def get_agent() -> TaskAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TaskAgent()
    return _agent_instance