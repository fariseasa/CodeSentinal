import json
import time
from datetime import datetime
from pathlib import Path

from agent.graph.graph import build_graph


SCENARIOS = [
    {
        "name": "basic_bug",
        "repo_path": "eval/demo_repos/basic_bug",
        "issue": (
            "The application crashes when the discount "
            "value is set to None."
        ),
    },
    {
        "name": "failing_test",
        "repo_path": "eval/demo_repos/failing_test",
        "issue": (
            "The calculate_total function produces an "
            "incorrect result for price and quantity."
        ),
    },
    {
        "name": "api_bug",
        "repo_path": "eval/demo_repos/api_bug",
        "issue": (
            "The API returns an incorrect value for the "
            "status field in the user response."
        ),
    },
    {
        "name": "regression_bug",
        "repo_path": "eval/demo_repos/regression_bug",
        "issue": (
            "The format_username function returns the wrong "
            "capitalization. The first letter should be uppercase."
        ),
    },
    {
        "name": "refactor_bug",
        "repo_path": "eval/demo_repos/refactor_bug",
        "issue": (
            "The get_first_item function crashes when an empty "
            "list is provided. It should return None."
        ),
    },
]


def run_evaluation():

    app = build_graph()

    results = []

    print("\n========== CODE SENTINEL EVALUATION ==========\n")

    for scenario in SCENARIOS:

        print(f"Running: {scenario['name']}")

        start_time = time.time()

        try:
            result = app.invoke(
                {
                    "repo_path": scenario["repo_path"],
                    "issue": scenario["issue"],
                    "retry_count": 0,
                    "max_retries": 3,
                }
            )

            execution_time = time.time() - start_time

            passed = (
                result.get("test_result") is not None
                and result["test_result"].passed
                and result.get("critic_verdict") is not None
                and result["critic_verdict"].approved
            )

            results.append(
                {
                    "name": scenario["name"],
                    "passed": passed,
                    "retries": result.get("retry_count", 0),
                    "time": round(execution_time, 2),
                }
            )

        except Exception as error:

            execution_time = time.time() - start_time

            print(f"ERROR: {error}")

            results.append(
                {
                    "name": scenario["name"],
                    "passed": False,
                    "retries": 0,
                    "time": round(execution_time, 2),
                    "error": str(error),
                }
            )

    return results


def calculate_summary(results):

    passed_count = sum(
        1 for result in results
        if result["passed"]
    )

    total = len(results)

    total_time = sum(
        result["time"]
        for result in results
    )

    success_rate = (
        (passed_count / total) * 100
        if total > 0
        else 0
    )

    average_time = (
        total_time / total
        if total > 0
        else 0
    )

    return {
        "total_scenarios": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "success_rate": round(success_rate, 2),
        "total_time": round(total_time, 2),
        "average_time": round(average_time, 2),
    }


def print_summary(results):

    summary = calculate_summary(results)

    print("\n========== EVALUATION RESULTS ==========\n")

    print(
        f"{'Scenario':<20}"
        f"{'Result':<10}"
        f"{'Retries':<10}"
        f"{'Time (s)':<10}"
    )

    print("-" * 50)

    for result in results:

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{result['name']:<20}"
            f"{status:<10}"
            f"{result['retries']:<10}"
            f"{result['time']:.2f}"
        )

    print("\n----------------------------------------")

    print(
        f"Total Scenarios: "
        f"{summary['total_scenarios']}"
    )

    print(
        f"Passed: {summary['passed']}"
    )

    print(
        f"Failed: {summary['failed']}"
    )

    print(
        f"Success Rate: "
        f"{summary['success_rate']:.1f}%"
    )

    print(
        f"Total Time: "
        f"{summary['total_time']:.2f}s"
    )

    print(
        f"Average Time: "
        f"{summary['average_time']:.2f}s"
    )


def save_results(results):

    summary = calculate_summary(results)

    output_dir = (
        Path(__file__).parent / "results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir / "evaluation_results.json"
    )

    evaluation_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "scenarios": results,
    }

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evaluation_data,
            file,
            indent=4,
        )

    print(
        f"\nResults saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":

    results = run_evaluation()

    print_summary(results)

    save_results(results)