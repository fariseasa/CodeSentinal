from agent.graph import graph as graph_module

from shared.schemas import (
    CriticVerdict,
    Hypothesis,
    IssueTask,
    Patch,
    RepoMap,
    RetrievedCode,
    TestResult,
)


def test_full_retry_graph(monkeypatch):

    attempt_counter = {
        "patch": 0,
        "workspace": 0,
        "tests": 0,
        "critic": 0,
    }

    # -----------------------------------------
    # Fake Issue Understanding
    # -----------------------------------------

    def fake_issue_node(state):
        return {
            "issue_task": IssueTask(
                issue_description="Demo bug",
                goals=["Fix the bug"],
                suspected_files=[],
            )
        }

    # -----------------------------------------
    # Fake Repository Analysis
    # -----------------------------------------

    def fake_repo_node(state):
        return {
            "repo_map": RepoMap(
                files=["calculator.py"],
                modules=["calculator"],
                dependencies=[],
                functions=["get_final_price"],
                classes=[],
            )
        }

    # -----------------------------------------
    # Fake Retrieval
    # -----------------------------------------

    def fake_retrieval_node(state):
        return {
            "retrieved_code": [
                RetrievedCode(
                    file_path="calculator.py::get_final_price",
                    content="demo code",
                    relevance_score=1.0,
                )
            ]
        }

    # -----------------------------------------
    # Fake Investigation
    # -----------------------------------------

    def fake_investigation_node(state):
        return {
            "hypothesis": Hypothesis(
                explanation="Demo root cause",
                confidence=0.95,
                suspected_files=["calculator.py"],
            )
        }

    # -----------------------------------------
    # Fake Patch Generation
    # -----------------------------------------

    def fake_patch_generation_node(state):

        attempt_counter["patch"] += 1

        if attempt_counter["patch"] == 1:
            diff = "BAD PATCH"
        else:
            diff = "GOOD PATCH"

        return {
            "patch": Patch(
                file_path="calculator.py",
                diff=diff,
            )
        }

    # -----------------------------------------
    # Fake Workspace
    # -----------------------------------------

    def fake_workspace_node(state):

        attempt_counter["workspace"] += 1

        return {
            "workspace_path": (
                f"fake_workspace_"
                f"{attempt_counter['workspace']}"
            )
        }

    # -----------------------------------------
    # Fake Test Runner
    # -----------------------------------------

    def fake_test_runner_node(state):

        attempt_counter["tests"] += 1

        if attempt_counter["tests"] == 1:

            return {
                "test_result": TestResult(
                    passed=False,
                    logs="1 failed",
                    coverage_delta=0.0,
                )
            }

        return {
            "test_result": TestResult(
                passed=True,
                logs="2 passed",
                coverage_delta=0.0,
            )
        }

    # -----------------------------------------
    # Fake Critic
    # -----------------------------------------

    def fake_critic_node(state):

        attempt_counter["critic"] += 1

        return {
            "critic_verdict": CriticVerdict(
                approved=True,
                reasoning="Good patch",
                retry=False,
            )
        }

    # -----------------------------------------
    # Fake Report
    # -----------------------------------------

    def fake_report_node(state):

        return {
            "report": "Final report generated"
        }

    # -----------------------------------------
    # Patch the functions used by graph.py
    # -----------------------------------------

    monkeypatch.setattr(
        graph_module,
        "issue_understanding_node",
        fake_issue_node,
    )

    monkeypatch.setattr(
        graph_module,
        "repository_analysis_node",
        fake_repo_node,
    )

    monkeypatch.setattr(
        graph_module,
        "retrieval_node",
        fake_retrieval_node,
    )

    monkeypatch.setattr(
        graph_module,
        "investigation_node",
        fake_investigation_node,
    )

    monkeypatch.setattr(
        graph_module,
        "patch_generation_node",
        fake_patch_generation_node,
    )

    monkeypatch.setattr(
        graph_module,
        "workspace_node",
        fake_workspace_node,
    )

    monkeypatch.setattr(
        graph_module,
        "test_runner_node",
        fake_test_runner_node,
    )

    monkeypatch.setattr(
        graph_module,
        "critic_node",
        fake_critic_node,
    )

    monkeypatch.setattr(
        graph_module,
        "report_node",
        fake_report_node,
    )

    # -----------------------------------------
    # Build and run the real LangGraph structure
    # -----------------------------------------

    app = graph_module.build_graph()

    result = app.invoke(
        {
            "repo_path": "fake_repo",
            "issue": "Demo bug",
            "retry_count": 0,
            "max_retries": 3,
        }
    )

    # -----------------------------------------
    # Assertions
    # -----------------------------------------

    assert result["report"] == (
        "Final report generated"
    )

    assert result["retry_count"] == 1

    assert attempt_counter["patch"] == 2

    assert attempt_counter["workspace"] == 2

    assert attempt_counter["tests"] == 2

    assert attempt_counter["critic"] == 1