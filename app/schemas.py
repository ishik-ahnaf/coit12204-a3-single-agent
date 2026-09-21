from pydantic import BaseModel, Field
from typing import Optional


class DueDateRequest(BaseModel):
    task_title: str = Field(..., min_length=1, max_length=200)
    task_description: Optional[str] = Field(default="", max_length=1000)
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$")


class DueDateResponse(BaseModel):
    suggested_date: str
    reasoning: str
    confidence: str
    state_snapshot: dict


class PriorityRequest(BaseModel):
    task_title: str = Field(..., min_length=1, max_length=200)
    task_description: Optional[str] = Field(default="", max_length=1000)


class PriorityResponse(BaseModel):
    priority: str
    confidence: str
    reasoning: str
    state_snapshot: dict


class SummaryRequest(BaseModel):
    tasks: list[str] = Field(..., min_length=1, max_length=50)


class SummaryResponse(BaseModel):
    summary: str
    task_count: int
    state_snapshot: dict