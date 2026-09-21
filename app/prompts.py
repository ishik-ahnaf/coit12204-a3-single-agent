"""Prompt templates for the agent."""

from langchain_core.prompts import PromptTemplate


REACT_PROMPT = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)

ACTIVE_PROMPT = REACT_PROMPT

PROMPT_REFINEMENTS = [
    {
        "iteration": 1,
        "change": "Baseline prompt with no format constraints",
        "failure_observed": "Agent produced verbose output; tool results repeated verbatim",
        "fix": "Switched to structured ReAct format with explicit scaffolding",
    },
    {
        "iteration": 2,
        "change": "Added explicit tool-use instruction in system message",
        "failure_observed": "Agent still hallucinated task data without calling tools",
        "fix": "Adopted LangChain's official ReAct template which enforces format",
    },
    {
        "iteration": 3,
        "change": "Enforced ReAct format with required variables (tools, tool_names, agent_scratchpad)",
        "failure_observed": "None significant after this change",
        "fix": "N/A (current version)",
    },
]