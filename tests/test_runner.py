from execution.workspace import Workspace
from execution.patch_applier import PatchApplier
from execution.test_runner import TestRunner


def test_test_runner():

    workspace = Workspace(
        "eval/demo_repos/basic_bug"
    )

    workspace_path = workspace.create()

    try:

        patch = """*** Begin Patch
*** Update File: calculator.py
@@
-def get_final_price(price, discount):
-    if discount is None:
-        return calculate_discount(price, discount)
-
-    return calculate_discount(price, discount)
+def get_final_price(price, discount):
+    if discount is None:
+        return price
+
+    return calculate_discount(price, discount)
*** End Patch
"""

        applier = PatchApplier()

        applier.apply(
            workspace_path,
            "calculator.py",
            patch,
        )

        runner = TestRunner()

        result = runner.run(
            workspace_path
        )

        assert result.passed is True

        assert "passed" in result.logs

    finally:

        workspace.cleanup()