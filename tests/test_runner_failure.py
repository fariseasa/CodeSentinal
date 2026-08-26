from execution.workspace import Workspace
from execution.patch_applier import PatchApplier
from execution.test_runner import TestRunner


def test_test_runner_detects_failure():

    workspace = Workspace(
        "eval/demo_repos/basic_bug"
    )

    workspace_path = workspace.create()

    try:

        # Intentionally BAD patch
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
+        return price + "wrong"
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

        # The bad patch must fail the tests
        assert result.passed is False

        # Pytest should have produced failure/error information
        assert result.logs

    finally:

        workspace.cleanup()