from typing import List, Optional
from pydantic import BaseModel


class RepoMap(BaseModel):
    files: List[str]
    modules: List[str]
    dependencies: List[str]
    functions: List[str]
    classes: List[str]


class IssueTask(BaseModel):
    issue_description: str
    goals: List[str]
    suspected_files: List[str] = []


class RetrievedCode(BaseModel):
    file_path: str
    content: str
    relevance_score: float


class Hypothesis(BaseModel):
    explanation: str
    confidence: float
    suspected_files: List[str]


class Patch(BaseModel):
    file_path: str
    diff: str


class TestResult(BaseModel):
    passed: bool
    logs: str
    coverage_delta: Optional[float] = None


class CriticVerdict(BaseModel):
    approved: bool
    reasoning: str
    retry: bool


class PRReport(BaseModel):
    root_cause: str
    changes: str
    tests: str
    remaining_risks: List[str]