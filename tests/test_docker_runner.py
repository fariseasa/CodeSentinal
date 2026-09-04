from execution.test_runner import TestRunner as DockerTestRunner


def test_docker_runner(tmp_path):

    project = tmp_path

    (project / "test_example.py").write_text(
        "def test_example():\n"
        "    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )

    runner = DockerTestRunner()

    result = runner.run(
        workspace_path=str(project)
    )

    assert result.passed is True
    assert "1 passed" in result.logs