from agent.analyzer.repository_analyzer import RepositoryAnalyzer


def test_repository_analyzer():

    analyzer = RepositoryAnalyzer(
        "eval/demo_repos/basic_bug"
    )

    repo_map = analyzer.analyze()

    assert "app.py" in repo_map.files
    assert "calculator.py" in repo_map.files
    assert "utils.py" in repo_map.files

    assert "calculate_discount" in repo_map.functions
    assert "get_final_price" in repo_map.functions
    assert "format_price" in repo_map.functions

    assert "app" in repo_map.modules
    assert "calculator" in repo_map.modules
    assert "utils" in repo_map.modules