from agent.graph.graph import (
    critic_router,
    route_test_result,
)
from agent.graph.nodes import retry_node

from shared.schemas import (
    CriticVerdict,
    TestResult,
)


def test_retry_node_increments_count():

    state = {
        "retry_count": 0,
        "max_retries": 3,
    }

    result = retry_node(state)

    assert result["retry_count"] == 1


def test_failed_tests_trigger_retry():

    state = {
        "test_result": TestResult(
            passed=False,
            logs="1 failed",
            coverage_delta=0.0,
        ),
        "retry_count": 0,
        "max_retries": 3,
    }

    route = route_test_result(state)

    assert route == "retry"


def test_passing_tests_go_to_critic():

    state = {
        "test_result": TestResult(
            passed=True,
            logs="2 passed",
            coverage_delta=0.0,
        ),
        "retry_count": 0,
        "max_retries": 3,
    }

    route = route_test_result(state)

    assert route == "critic"


def test_critic_approval_goes_to_report():

    state = {
        "critic_verdict": CriticVerdict(
            approved=True,
            reasoning="Patch fixes the bug and tests pass.",
            retry=False,
        ),
        "retry_count": 0,
        "max_retries": 3,
    }

    route = critic_router(state)

    assert route == "report"


def test_critic_rejection_triggers_retry():

    state = {
        "critic_verdict": CriticVerdict(
            approved=False,
            reasoning="Patch is incorrect.",
            retry=True,
        ),
        "retry_count": 0,
        "max_retries": 3,
    }

    route = critic_router(state)

    assert route == "retry"


def test_retry_limit_goes_to_report():

    state = {
        "test_result": TestResult(
            passed=False,
            logs="1 failed",
            coverage_delta=0.0,
        ),
        "retry_count": 3,
        "max_retries": 3,
    }

    route = route_test_result(state)
    assert route == "report"