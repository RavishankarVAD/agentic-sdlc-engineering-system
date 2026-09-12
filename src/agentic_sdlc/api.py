from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .orchestrator import WorkflowOrchestrator

app = FastAPI(title="Agentic SDLC Engineering System", version="0.1.0")
orchestrator = WorkflowOrchestrator()


class RunRequest(BaseModel):
    requirement: str
    codebase: str | None = None
    approve: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/runs")
def run_workflow(body: RunRequest):
    outcome = orchestrator.run(body.requirement, body.codebase, body.approve)
    result = outcome.to_dict()
    result["artifacts"] = sorted(outcome.artifacts.keys())
    return result
