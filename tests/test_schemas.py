from shared.schemas import (
    RepoMap,
    IssueTask,
    RetrievedCode,
    Hypothesis,
    Patch,
    TestResult,
    CriticVerdict,
    PRReport,
)


def test_repo_map():
    repo_map = RepoMap(
        files=["app.py", "utils.py"],
        modules=["app", "utils"],
        dependencies=["fastapi"],
        functions=["main"],
        classes=[]
    )

    assert "app.py" in repo_map.files


def test_issue_task():
    issue = IssueTask(
        issue_description="Application crashes when user is not found",
        goals=["Find the source of the crash", "Create a fix"]
    )

    assert len(issue.goals) == 2


def test_patch():
    patch = Patch(
        file_path="app.py",
        diff="- return user.name\n+ return user.name if user else None"
    )

    assert patch.file_path == "app.py"