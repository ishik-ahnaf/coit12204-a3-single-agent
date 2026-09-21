"""Structured-output summary agent (bonus extension)."""

from dotenv import load_dotenv
load_dotenv()

import json
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("summary_agent")


SUMMARY_PROMPT = PromptTemplate.from_template(
    """Given this list of tasks:
{tasks}

Return ONLY a JSON object with this exact structure, no other text:
{{
  "total": <number>,
  "high_priority": [<list of task strings>],
  "normal_priority": [<list of task strings>],
  "recommendation": "<one sentence>"
}}"""
)


class SummaryAgent:
    """Second agent that returns strict JSON structured output."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0.0,
            response_mime_type="application/json",
        )
        self.chain = SUMMARY_PROMPT | self.llm
        logger.info("SummaryAgent initialised (JSON structured output)")

    def summarise(self, tasks: list) -> dict:
        """Return a structured summary of the given tasks."""
        formatted = "\n".join(f"- {t}" for t in tasks)
        try:
            result = self.chain.invoke({"tasks": formatted})
            content = result.content if hasattr(result, "content") else str(result)
            parsed = json.loads(content)
            logger.info("SummaryAgent produced structured output for %d tasks", len(tasks))
            return parsed
        except Exception as e:
            logger.error("SummaryAgent failed: %s", str(e))
            return {
                "error": f"{type(e).__name__}: {str(e)}",
                "total": len(tasks),
                "high_priority": [],
                "normal_priority": tasks,
                "recommendation": "Structured summary unavailable due to an error.",
            }


_summary_agent = None


def get_summary_agent() -> SummaryAgent:
    global _summary_agent
    if _summary_agent is None:
        _summary_agent = SummaryAgent()
    return _summary_agent