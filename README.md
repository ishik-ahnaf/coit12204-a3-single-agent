# COIT12204 Assessment 3 — Single Agent Systems

A LangChain-based single agent for task management, integrated with FastAPI
and tested with pytest.

**Student:** Mushfiq Ahnaf Ishik
**Student ID:** 12282758
**Unit:** COIT12204 AI-Assisted Software Development
**Assessment:** 3 — Individual Practical Application of Single Agent Systems
**Campus:** Sydney
**Tutor:** Farzad Sanati

---

## Overview

This project implements a **single intelligent agent** that:
- Uses LangChain's ReAct pattern with two tools (`lookup_task`, `summarise_tasks`)
- Maintains internal state across runs (`AgentState`)
- Persists state to `agent_state.json` (bonus extension)
- Includes a second structured-output agent (bonus extension)
- Is exposed via FastAPI endpoints
- Is fully tested with pytest (28 tests, all mocked)
- Uses Google Gemini (`gemini-3.6-flash`) as the LLM backend

---

## Setup

### 1. Clone and enter the project

```bash
cd "Single Agent Systems"