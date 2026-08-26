from agent.critic.critic_agent import CriticAgent

from shared.schemas import (
    Hypothesis,
    Patch,
    TestResult,
)


def test_critic_approves_passing_patch():

    hypothesis = Hypothesis(
        explanation=(
            "discount is None and is passed into "
            "calculate_discount, causing a TypeError."
        ),
        confidence=0.9,
        suspected_files=[
            "calculator.py"
        ],
    )

    patch = Patch(
        file_path="calculator.py",
        diff="""*** Begin Patch
*** Update File: calculator.py
@@
-        return calculate_discount(price, discount)
+        return price
*** End Patch
""",
    )

    test_result = TestResult(
        passed=True,
        logs="2 passed",
        coverage_delta=0.0,
    )

    critic = CriticAgent()

    verdict = critic.evaluate(
        hypothesis=hypothesis,
        patch=patch,
        test_result=test_result,
    )

    assert verdict.approved is True
    assert verdict.retry is False
    assert verdict.reasoning




    def test_critic_rejects_failing_patch():

        hypothesis = Hypothesis(
            explanation=(
               "discount is None and is passed into "
               "calculate_discount, causing a TypeError."
            ),
            confidence=0.9,
            suspected_files=[
                "calculator.py"
            ],
        )

        patch = Patch(
            file_path="calculator.py",
            diff="""*** Begin Patch
    *** Update File: calculator.py
    @@
    -        return calculate_discount(price, discount)
    +        return price + "wrong"
    *** End Patch
    """,
        )

        test_result = TestResult(
            passed=False,
            logs=(
                "TypeError: unsupported operand type(s)"
            ),
           coverage_delta=0.0,
        )

        critic = CriticAgent()

        verdict = critic.evaluate(
            hypothesis=hypothesis,
            patch=patch,
            test_result=test_result,
            test_code="""
        def test_discount():
            assert get_final_price(100, 0.10) == 90


        def test_no_discount():
            assert get_final_price(100, None) == 100
            """,
        )

        assert verdict.approved is False
        assert verdict.retry is True
        assert verdict.reasoning  