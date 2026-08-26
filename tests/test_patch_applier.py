from pathlib import Path

from execution.workspace import Workspace
from execution.patch_applier import PatchApplier


def test_patch_applier():

    workspace = Workspace(
        "eval/demo_repos/basic_bug"
    )

    workspace_path = workspace.create()

    try:

        patch = """*** Begin Patch
*** Update File: calculator.py
@@
-        return calculate_discount(price, discount)
+        return price
*** End Patch
"""

        applier = PatchApplier()

        applier.apply(
            workspace_path,
            "calculator.py",
            patch,
        )

        calculator = Path(
            workspace_path
        ) / "calculator.py"

        content = calculator.read_text(
            encoding="utf-8"
        )

        assert "return price" in content

        assert (
        content.count(
        "return calculate_discount(price, discount)"
        ) == 1
)

    finally:

        workspace.cleanup()