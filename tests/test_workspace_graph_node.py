from agent.graph.nodes import workspace_node
from shared.schemas import Patch


def test_workspace_graph_node():

    state = {
        "repo_path": "eval/demo_repos/basic_bug",

        "patch": Patch(
            file_path="calculator.py",
            diff="""*** Begin Patch
*** Update File: calculator.py
@@
 def get_final_price(price, discount):
     if discount is None:
-        return calculate_discount(price, discount)
+        return price

     return calculate_discount(price, discount)
*** End Patch
""",
        ),
    }

    result = workspace_node(state)

    assert "workspace_path" in result

    workspace_path = result["workspace_path"]

    assert workspace_path

    calculator_path = (
        f"{workspace_path}/calculator.py"
    )

    with open(
        calculator_path,
        "r",
        encoding="utf-8",
    ) as file:

        content = file.read()

    assert "return price" in content
    assert (
        "return calculate_discount(price, discount)"
        in content
    )