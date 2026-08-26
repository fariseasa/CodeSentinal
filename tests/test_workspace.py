from pathlib import Path

from execution.workspace import Workspace


def test_workspace():

    source = "eval/demo_repos/basic_bug"

    workspace = Workspace(source)

    workspace_path = workspace.create()

    try:

        workspace_dir = Path(
            workspace_path
        )

        assert workspace_dir.exists()

        assert (
            workspace_dir / "calculator.py"
        ).exists()

        assert (
            workspace_dir / "tests"
        ).exists()

        # Make sure the workspace is
        # actually separate from the source repo.
        assert workspace_dir != Path(
            source
        ).resolve()

    finally:

        workspace.cleanup()

    assert not workspace_dir.exists()