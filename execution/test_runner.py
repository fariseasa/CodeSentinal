import subprocess
import uuid
from pathlib import Path

from shared.schemas import TestResult


class TestRunner:
    __test__ = False

    def run(self, workspace_path: str) -> TestResult:
        workspace = Path(workspace_path).resolve()

        if not workspace.exists():
            raise FileNotFoundError(
                f"Workspace not found: {workspace}"
            )

        image_name = f"codesentinel-test-{uuid.uuid4().hex[:8]}"

        try:
            dockerfile = self._create_dockerfile(workspace)

            # 1. Build the temporary Docker image
            build_result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-f",
                    str(dockerfile),
                    "-t",
                    image_name,
                    str(workspace),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )

            if build_result.returncode != 0:
                logs = (
                    "Docker image build failed.\n\n"
                    + build_result.stdout
                    + "\n"
                    + build_result.stderr
                )

                return TestResult(
                    passed=False,
                    logs=logs,
                    coverage_delta=0.0,
                )

            # 2. Run tests inside the Docker sandbox
            test_result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    image_name,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )

            passed = test_result.returncode == 0

            logs = (
                test_result.stdout
                + "\n"
                + test_result.stderr
            )

            return TestResult(
                passed=passed,
                logs=logs,
                coverage_delta=0.0,
            )

        except subprocess.TimeoutExpired as error:
            return TestResult(
                passed=False,
                logs=f"Docker execution timed out: {error}",
                coverage_delta=0.0,
            )

        finally:
            self._remove_image(image_name)

            if "dockerfile" in locals() and dockerfile.exists():
                dockerfile.unlink()

    def _create_dockerfile(self, workspace: Path) -> Path:
        requirements = workspace / "requirements.txt"

        if requirements.exists():
            install_step = (
                "COPY requirements.txt /workspace/requirements.txt\n"
                "RUN pip install --no-cache-dir "
                "-r /workspace/requirements.txt"
            )
        else:
            install_step = (
                "RUN pip install --no-cache-dir pytest"
            )

        dockerfile_content = f"""FROM python:3.10-slim

WORKDIR /workspace

RUN pip install --no-cache-dir pytest

{install_step}

COPY . /workspace

CMD ["python", "-m", "pytest"]
"""

        dockerfile = (
            workspace
            / f".codesentinel_dockerfile_{uuid.uuid4().hex}"
        )

        dockerfile.write_text(
            dockerfile_content,
            encoding="utf-8",
        )

        return dockerfile

    def _remove_image(self, image_name: str) -> None:
        subprocess.run(
            [
                "docker",
                "image",
                "rm",
                "-f",
                image_name,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )