import subprocess
import sys
from pathlib import Path

from shared.schemas import TestResult


class TestRunner:

    def run(
        self,
        workspace_path: str,
    ) -> TestResult:

        workspace = Path(workspace_path)

        result = subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=60,
        )

        passed = result.returncode == 0

        logs = (
            result.stdout
            + "\n"
            + result.stderr
        )

        return TestResult(
            passed=passed,
            logs=logs,
            coverage_delta=0.0,
        )