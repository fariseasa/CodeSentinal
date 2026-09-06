from typing import TypedDict, List, Optional

from shared.schemas import (
    RepoMap,
    IssueTask,
    RetrievedCode,
    Hypothesis,
    Patch,
    TestResult,
    CriticVerdict,
)


class AgentState(TypedDict, total=False):

    # Input
    repo_path: str
    issue: str

    # Analysis
    repo_map: RepoMap
    issue_task: IssueTask
    retrieved_code: List[RetrievedCode]
    hypothesis: Hypothesis

    # Patch
    patch: Patch

    # Execution
    workspace_path: str
    test_result: TestResult

    # Critic
    critic_verdict: CriticVerdict

    # Retry control
    retry_count: int
    max_retries: int

    # Final output
    report: str

    retry_history: list[dict]