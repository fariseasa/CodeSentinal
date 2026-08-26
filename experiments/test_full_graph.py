from agent.graph.graph import build_graph


def main():

    app = build_graph()

    result = app.invoke(
        {
            "repo_path": "eval/demo_repos/refactor_bug",
            "issue": (
                "The get_first_item function crashes when an empty "
                "list is provided. It should return None for an empty list."
            ),
            "retry_count": 0,
            "max_retries": 3,
        }
    )

    print("\n========== FINAL STATE ==========\n")

    print("Issue Task:")
    print(result.get("issue_task"))

    print("\nHypothesis:")
    print(result.get("hypothesis"))

    print("\nPatch:")
    print(result.get("patch"))

    print("\nTest Result:")
    print(result.get("test_result"))

    print("\nCritic Verdict:")
    print(result.get("critic_verdict"))

    print("\nReport:")
    print(result.get("report"))


if __name__ == "__main__":
    main()