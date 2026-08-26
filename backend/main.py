from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.graph.graph import build_graph


app = FastAPI(
    title="CodeSentinel API",
    description="AI-powered software debugging agent",
    version="0.1.0",
)


runs = {}


class RunRequest(BaseModel):
    repo_path: str
    issue: str
    max_retries: int = 3


class RunResponse(BaseModel):
    run_id: str
    status: str


class RunResult(BaseModel):
    run_id: str
    status: str
    issue: str
    root_cause: str | None = None
    confidence: float | None = None
    changed_file: str | None = None
    patch: str | None = None
    tests_passed: bool | None = None
    test_logs: str | None = None
    critic_approved: bool | None = None
    critic_reasoning: str | None = None
    retry_count: int = 0
    report: str | None = None


@app.get("/")
def root():

    return {
        "service": "CodeSentinel",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "codesentinel",
    }


@app.post("/run", response_model=RunResponse)
def create_run(request: RunRequest):

    run_id = str(uuid4())

    runs[run_id] = {
        "status": "running",
        "issue": request.issue,
        "result": None,
    }

    try:

        graph = build_graph()

        result = graph.invoke(
            {
                "repo_path": request.repo_path,
                "issue": request.issue,
                "retry_count": 0,
                "max_retries": request.max_retries,
            }
        )

        hypothesis = result.get("hypothesis")
        patch = result.get("patch")
        test_result = result.get("test_result")
        critic = result.get("critic_verdict")

        clean_result = {
            "run_id": run_id,
            "status": "completed",
            "issue": request.issue,
            "root_cause": (
                hypothesis.explanation
                if hypothesis
                else None
            ),
            "confidence": (
                hypothesis.confidence
                if hypothesis
                else None
            ),
            "changed_file": (
                patch.file_path
                if patch
                else None
            ),
            "patch": (
                patch.diff
                if patch
                else None
            ),
            "tests_passed": (
                test_result.passed
                if test_result
                else None
            ),
            "test_logs": (
                test_result.logs
                if test_result
                else None
            ),
            "critic_approved": (
                critic.approved
                if critic
                else None
            ),
            "critic_reasoning": (
                critic.reasoning
                if critic
                else None
            ),
            "retry_count": result.get(
                "retry_count",
                0,
            ),
            "report": result.get(
                "report"
            ),
        }

        runs[run_id]["status"] = "completed"
        runs[run_id]["result"] = clean_result

    except Exception as error:

        runs[run_id]["status"] = "failed"

        runs[run_id]["result"] = {
            "run_id": run_id,
            "status": "failed",
            "issue": request.issue,
            "error": str(error),
        }

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    return RunResponse(
        run_id=run_id,
        status="completed",
    )


@app.get(
    "/run/{run_id}",
    response_model=RunResult,
)
def get_run(run_id: str):

    run = runs.get(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    if run["result"] is None:

        raise HTTPException(
            status_code=202,
            detail="Run is still in progress",
        )

    return run["result"]