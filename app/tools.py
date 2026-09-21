"""LangChain tools for the agent."""

from langchain_core.tools import tool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_tools")


TASK_DATABASE = {
    "assignment": {"title": "COIT12204 Assessment 3", "priority": "high", "due": "Week 9 Friday"},
    "report": {"title": "Technical Report", "priority": "medium", "due": "Week 9 Friday"},
    "video": {"title": "Demonstration Video", "priority": "medium", "due": "Week 9 Friday"},
}


@tool
def lookup_task(query: str) -> str:
    """Look up a task in the internal task database by keyword."""
    query_lower = query.lower()
    matches = []
    for key, task in TASK_DATABASE.items():
        if query_lower in key or query_lower in task["title"].lower():
            matches.append(task)

    if not matches:
        return f"No task found matching '{query}'. Available keywords: {', '.join(TASK_DATABASE.keys())}"

    result = "\n".join(
        f"- {t['title']} (priority: {t['priority']}, due: {t['due']})" for t in matches
    )
    logger.info(f"lookup_task called with query='{query}', found {len(matches)} match(es)")
    return f"Found {len(matches)} task(s):\n{result}"


@tool
def summarise_tasks(task_list: str) -> str:
    """Summarise a list of tasks into a concise weekly overview."""
    if "," in task_list:
        tasks = [t.strip() for t in task_list.split(",") if t.strip()]
    else:
        tasks = [t.strip() for t in task_list.split("\n") if t.strip()]

    if not tasks:
        return "No tasks provided to summarise."

    high_keywords = ["exam", "assessment", "deadline", "urgent", "high"]
    high = [t for t in tasks if any(k in t.lower() for k in high_keywords)]
    normal = [t for t in tasks if t not in high]

    lines = ["Weekly Task Summary:"]
    if high:
        lines.append(f"  High priority ({len(high)}): {', '.join(high)}")
    if normal:
        lines.append(f"  Normal priority ({len(normal)}): {', '.join(normal)}")
    lines.append(f"  Total tasks: {len(tasks)}")

    logger.info(f"summarise_tasks called with {len(tasks)} task(s)")
    return "\n".join(lines)


ALL_TOOLS = [lookup_task, summarise_tasks]