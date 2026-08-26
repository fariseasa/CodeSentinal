import shutil
import tempfile
from pathlib import Path


class Workspace:

    def __init__(self, source_repo: str):

        self.source_repo = Path(
            source_repo
        ).resolve()

        self.path = None

    def create(self) -> str:

        if not self.source_repo.exists():
            raise FileNotFoundError(
                f"Repository not found: {self.source_repo}"
            )

        temp_dir = tempfile.mkdtemp(
            prefix="codesentinel_"
        )

        workspace_path = Path(temp_dir)

        shutil.copytree(
            self.source_repo,
            workspace_path,
            dirs_exist_ok=True,
        )

        self.path = workspace_path

        return str(workspace_path)

    def cleanup(self):

        if self.path and self.path.exists():

            shutil.rmtree(
                self.path,
                ignore_errors=True
            )

            self.path = None