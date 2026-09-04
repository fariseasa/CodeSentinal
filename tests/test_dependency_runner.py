from execution.test_runner import TestRunner


def test_dependency_project():
    runner = TestRunner()

    result = runner.run(
        "eval/demo_repos/dependency_test"
    )

    assert result.passed is True