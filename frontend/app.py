import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="CodeSentinel",
    page_icon="🛡️",
    layout="wide",
)


st.title("🛡️ CodeSentinel")
st.caption(
    "AI-powered software debugging and self-correcting patch generation"
)

st.divider()

# -----------------------------
# Input
# -----------------------------

st.subheader("Run a Debugging Investigation")

repo_path = st.text_input(
    "Repository Path",
    value="eval/demo_repos/basic_bug",
)

issue = st.text_area(
    "Bug Report",
    value=(
        "The application crashes when the discount "
        "value is set to None."
    ),
    height=120,
)

max_retries = st.number_input(
    "Maximum Retries",
    min_value=0,
    max_value=5,
    value=3,
    step=1,
)

run_button = st.button(
    "🚀 Analyze & Fix",
    type="primary",
)


# -----------------------------
# Run
# -----------------------------

if run_button:

    if not repo_path.strip():
        st.error("Repository path is required.")
        st.stop()

    if not issue.strip():
        st.error("Bug report is required.")
        st.stop()

    payload = {
        "repo_path": repo_path,
        "issue": issue,
        "max_retries": max_retries,
    }

    try:

        with st.spinner(
            "CodeSentinel is investigating the repository..."
        ):

            response = requests.post(
                f"{API_URL}/run",
                json=payload,
                timeout=300,
            )

        if response.status_code != 200:

            st.error(
                f"Backend error: {response.text}"
            )
            st.stop()

        run_info = response.json()
        run_id = run_info["run_id"]

        result_response = requests.get(
            f"{API_URL}/run/{run_id}",
            timeout=30,
        )

        if result_response.status_code != 200:

            st.error(
                f"Could not retrieve result: "
                f"{result_response.text}"
            )
            st.stop()

        result = result_response.json()

        st.success(
            f"Run completed successfully — {run_id}"
        )

        st.divider()

        # -----------------------------
        # Summary metrics
        # -----------------------------

        st.subheader("Investigation Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            confidence = result.get("confidence")

            if confidence is not None:
                st.metric(
                    "Confidence",
                    f"{confidence:.0%}",
                )
            else:
                st.metric(
                    "Confidence",
                    "N/A",
                )

        with col2:
            tests_passed = result.get(
                "tests_passed"
            )

            st.metric(
                "Tests",
                "PASS"
                if tests_passed
                else "FAIL",
            )

        with col3:
            critic_approved = result.get(
                "critic_approved"
            )

            st.metric(
                "Critic",
                "APPROVED"
                if critic_approved
                else "REJECTED",
            )

        with col4:
            st.metric(
                "Retries",
                result.get(
                    "retry_count",
                    0,
                ),
            )

        # -----------------------------
        # Root Cause
        # -----------------------------

        st.subheader("🔍 Root Cause")

        st.write(
            result.get(
                "root_cause",
                "No root cause available.",
            )
        )

        # -----------------------------
        # Changed File
        # -----------------------------

        st.subheader("📁 Changed File")

        changed_file = result.get(
            "changed_file"
        )

        if changed_file:
            st.code(changed_file)
        else:
            st.info("No changed file reported.")

        # -----------------------------
        # Patch
        # -----------------------------

        st.subheader("🩹 Generated Patch")

        patch = result.get("patch")

        if patch:
            st.code(
                patch,
                language="diff",
            )
        else:
            st.info("No patch generated.")

        # -----------------------------
        # Tests
        # -----------------------------

        st.subheader("🧪 Test Results")

        if result.get("tests_passed"):
            st.success("All tests passed.")
        else:
            st.error("Tests failed.")

        with st.expander("View Test Logs"):
            st.code(
                result.get(
                    "test_logs",
                    "No test logs available.",
                )
            )

        # -----------------------------
        # Critic
        # -----------------------------

        st.subheader("🤖 Critic Verdict")

        if result.get("critic_approved"):
            st.success("Patch approved.")
        else:
            st.error("Patch rejected.")

        st.write(
            result.get(
                "critic_reasoning",
                "No critic reasoning available.",
            )
        )

        # -----------------------------
        # Report
        # -----------------------------

        st.subheader("📄 Final PR Report")

        report = result.get("report")

        if report:
            st.markdown(report)
        else:
            st.info("No report available.")

    except requests.RequestException as error:

        st.error(
            f"Could not connect to CodeSentinel API: {error}"
        )