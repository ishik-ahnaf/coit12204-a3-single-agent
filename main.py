from dotenv import load_dotenv
load_dotenv()

"""FastAPI application exposing the TaskAgent via REST endpoints."""

import logging
import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.agent import get_agent
from app.summary_agent import get_summary_agent
from app.schemas import (
    DueDateRequest, DueDateResponse,
    PriorityRequest, PriorityResponse,
    SummaryRequest, SummaryResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi")

app = FastAPI(title="COIT12204 A3 - Task Agent API", version="1.0.0")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent_ready": True}


# ---------------------------------------------------------------------------
# Main ReAct agent endpoints
# ---------------------------------------------------------------------------
@app.post("/api/agent/suggest_due_date", response_model=DueDateResponse)
async def suggest_due_date(request: DueDateRequest):
    agent = get_agent()
    query = (
        f"Suggest a due date for this task: '{request.task_title}'. "
        f"Description: {request.task_description or 'none'}. Priority: {request.priority}."
    )
    result = agent.run(query)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    output = result["output"]
    date_match = re.search(r"(\d{4}-\d{2}-\d{2}|Week \d+|next \w+)", output)
    suggested = date_match.group(1) if date_match else "Not determined"

    return DueDateResponse(
        suggested_date=suggested,
        reasoning=output[:500],
        confidence="medium",
        state_snapshot=result["state_snapshot"],
    )


@app.post("/api/agent/classify_priority", response_model=PriorityResponse)
async def classify_priority(request: PriorityRequest):
    agent = get_agent()
    query = (
        f"Classify the priority of this task as low, medium, or high: "
        f"'{request.task_title}'. Description: {request.task_description or 'none'}."
    )
    result = agent.run(query)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    output = result["output"].lower()
    if "high" in output:
        priority = "high"
    elif "low" in output:
        priority = "low"
    else:
        priority = "medium"

    return PriorityResponse(
        priority=priority,
        confidence="medium",
        reasoning=result["output"][:500],
        state_snapshot=result["state_snapshot"],
    )


@app.post("/api/agent/weekly_summary", response_model=SummaryResponse)
async def weekly_summary(request: SummaryRequest):
    agent = get_agent()
    task_text = ", ".join(request.tasks)
    query = f"Summarise these tasks for my week: {task_text}"
    result = agent.run(query)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return SummaryResponse(
        summary=result["output"][:1000],
        task_count=len(request.tasks),
        state_snapshot=result["state_snapshot"],
    )


# ---------------------------------------------------------------------------
# Bonus: structured-output summary agent (second agent)
# ---------------------------------------------------------------------------
@app.post("/api/agent/structured_summary")
async def structured_summary(request: SummaryRequest):
    """
    Second agent: returns strict JSON structured output.
    Uses Gemini's JSON response mode instead of the ReAct pattern.
    """
    agent = get_summary_agent()
    return agent.summarise(request.tasks)


# ---------------------------------------------------------------------------
# State inspection
# ---------------------------------------------------------------------------
@app.get("/api/agent/state")
async def get_agent_state():
    agent = get_agent()
    return agent.get_state()


@app.post("/api/agent/reset")
async def reset_agent_state():
    agent = get_agent()
    agent.reset_state()
    return {"status": "reset", "state": agent.get_state()}
