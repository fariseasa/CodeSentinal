import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CodeSentinel",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ CodeSentinel")

st.caption(
    "AI-powered software debugging and self-correcting patch generation"
)

st.divider()


# ============================================================
# INPUT SECTION
# ============================================================

st.subheader("🚀 Run a Debugging Investigation")

repo_zip = st.file_uploader(
    "Upload Python Repository",
    type=["zip"],
    help=(
        "Upload a ZIP containing the Python repository. "
        "The repository should include its pytest tests."
    ),
)

issue = st.text_area(
    "🐛 Bug Report",
    placeholder=(
        "Example:\n"
        "The calculate_total function returns the wrong "
        "value when price and quantity are provided."
    ),
    height=140,
)

max_retries = st.number_input(
    "Maximum Retries",
    min_value=0,
    max_value=5,
    value=3,
    step=1,
    help=(
        "Maximum number of times CodeSentinel "
        "can retry a failed fix."
    ),
)


# ============================================================
# SHOW UPLOADED FILE
# ============================================================

if repo_zip is not None:

    file_size_mb = (
        len(repo_zip.getvalue())
        / (1024 * 1024)
    )

    st.success(
        f"Repository uploaded: **{repo_zip.name}** "
        f"({file_size_mb:.2f} MB)"
    )


st.divider()


# ============================================================
# RUN BUTTON
# ============================================================

run_button = st.button(
    "🚀 Analyze & Fix",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN CODE SENTINEL
# ============================================================

if run_button:

    # --------------------------------------------------------
    # Validate ZIP
    # --------------------------------------------------------

    if repo_zip is None:

        st.error(
            "Please upload a repository ZIP."
        )

        st.stop()

    # --------------------------------------------------------
    # Validate issue
    # --------------------------------------------------------

    if not issue.strip():

        st.error(
            "Please enter a bug report."
        )

        st.stop()

    # --------------------------------------------------------
    # Prepare request
    # --------------------------------------------------------

    files = {
        "repo_zip": (
            repo_zip.name,
            repo_zip.getvalue(),
            "application/zip",
        )
    }

    data = {
        "issue": issue.strip(),
        "max_retries": str(max_retries),
    }

    # --------------------------------------------------------
    # Call backend
    # --------------------------------------------------------

    try:

        with st.status(
            "CodeSentinel is investigating the repository...",
            expanded=True,
        ) as status:

            st.write(
                "📦 Uploading repository..."
            )

            st.write(
                "🔍 Analyzing repository..."
            )

            st.write(
                "🤖 Generating and validating a fix..."
            )

            response = requests.post(
                f"{API_URL}/run",
                files=files,
                data=data,
                timeout=300,
            )

            # ------------------------------------------------
            # Backend error
            # ------------------------------------------------

            if response.status_code != 200:

                status.update(
                    label="Investigation failed",
                    state="error",
                )

                st.error(
                    f"Backend error "
                    f"({response.status_code}): "
                    f"{response.text}"
                )

                st.stop()

            # ------------------------------------------------
            # Read run information
            # ------------------------------------------------

            run_info = response.json()

            run_id = run_info.get(
                "run_id"
            )

            if not run_id:

                status.update(
                    label="Invalid backend response",
                    state="error",
                )

                st.error(
                    "The backend did not return a run_id."
                )

                st.stop()

            st.write(
                f"✅ Run created: `{run_id}`"
            )

            # ------------------------------------------------
            # Retrieve result
            # ------------------------------------------------

            st.write(
                "📊 Retrieving final investigation result..."
            )

            result_response = requests.get(
                f"{API_URL}/run/{run_id}",
                timeout=30,
            )

            if result_response.status_code != 200:

                status.update(
                    label="Could not retrieve result",
                    state="error",
                )

                st.error(
                    "Could not retrieve the run result: "
                    f"{result_response.text}"
                )

                st.stop()

            result = result_response.json()

            status.update(
                label="Investigation completed",
                state="complete",
            )

        # ====================================================
        # RESULT HEADER
        # ====================================================

        st.success(
            "CodeSentinel completed the investigation — "
            f"`{run_id}`"
        )

        st.divider()

        st.subheader(
            "📊 Investigation Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        with col1:

            confidence = result.get(
                "confidence"
            )

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

        # ----------------------------------------------------
        # Tests
        # ----------------------------------------------------

        with col2:

            tests_passed = result.get(
                "tests_passed",
                False,
            )

            st.metric(
                "Tests",
                (
                    "PASS"
                    if tests_passed
                    else "FAIL"
                ),
            )

        # ----------------------------------------------------
        # Critic
        # ----------------------------------------------------

        with col3:

            critic_approved = result.get(
                "critic_approved",
                False,
            )

            st.metric(
                "Critic",
                (
                    "APPROVED"
                    if critic_approved
                    else "REJECTED"
                ),
            )

        # ----------------------------------------------------
        # Retries
        # ----------------------------------------------------

        with col4:

            st.metric(
                "Retries",
                result.get(
                    "retry_count",
                    0,
                ),
            )

        # ====================================================
        # ROOT CAUSE
        # ====================================================

        st.divider()

        st.subheader(
            "🔍 Root Cause"
        )

        root_cause = result.get(
            "root_cause"
        )

        if root_cause:

            st.write(
                root_cause
            )

        else:

            st.info(
                "No root cause was reported."
            )

        # ====================================================
        # CHANGED FILE
        # ====================================================

        st.subheader(
            "📁 Changed File"
        )

        changed_file = result.get(
            "changed_file"
        )

        if changed_file:

            st.code(
                changed_file,
                language="text",
            )

        else:

            st.info(
                "No changed file reported."
            )

        # ====================================================
        # GENERATED PATCH
        # ====================================================

        st.subheader(
            "🩹 Generated Patch"
        )

        patch = result.get(
            "patch"
        )

        if patch:

            st.code(
                patch,
                language="diff",
            )

        else:

            st.info(
                "No patch generated."
            )

        # ====================================================
        # TEST RESULTS
        # ====================================================

        st.subheader(
            "🧪 Test Results"
        )

        if tests_passed:

            st.success(
                "✅ All tests passed."
            )

        else:

            st.error(
                "❌ Tests failed."
            )

        with st.expander(
            "View Test Logs"
        ):

            st.code(
                result.get(
                    "test_logs",
                    "No test logs available.",
                ),
                language="text",
            )

        # ====================================================
        # CRITIC
        # ====================================================

        st.subheader(
            "🤖 Critic Verdict"
        )

        if critic_approved:

            st.success(
                "✅ Patch approved."
            )

        else:

            st.error(
                "❌ Patch rejected."
            )

        critic_reasoning = result.get(
            "critic_reasoning"
        )

        if critic_reasoning:

            st.write(
                critic_reasoning
            )

        else:

            st.info(
                "No critic reasoning available."
            )

        # ====================================================
        # FINAL REPORT
        # ====================================================

        st.subheader(
            "📄 Final PR Report"
        )

        report = result.get(
            "report"
        )

        if report:

            st.markdown(
                report
            )

        else:

            st.info(
                "No final report available."
            )

        # ====================================================
        # DOWNLOAD PATCHED REPOSITORY
        # ====================================================

        st.divider()

        st.subheader(
            "📦 Fixed Repository"
        )

        if result.get(
            "patched_zip_available"
        ):

            st.success(
                "CodeSentinel has created "
                "the patched repository."
            )

            download_url = (
                f"{API_URL}/run/"
                f"{run_id}/download"
            )

            try:

                download_response = requests.get(
                    download_url,
                    timeout=30,
                )

                if download_response.status_code == 200:

                    st.download_button(
                        label=(
                            "⬇️ Download "
                            "Patched Repository"
                        ),
                        data=download_response.content,
                        file_name=(
                            "codesentinel_fixed_"
                            f"{run_id}.zip"
                        ),
                        mime="application/zip",
                        use_container_width=True,
                    )

                else:

                    st.error(
                        "Could not retrieve "
                        "the patched repository."
                    )

            except requests.RequestException as error:

                st.error(
                    f"Download failed: {error}"
                )

        else:

            st.info(
                "No patched repository is "
                "available for this run."
            )

    # ========================================================
    # REQUEST ERRORS
    # ========================================================

    except requests.Timeout:

        st.error(
            "The CodeSentinel API took "
            "too long to respond."
        )

    except requests.ConnectionError:

        st.error(
            "Could not connect to the "
            "CodeSentinel API. "
            "Make sure the FastAPI backend "
            "is running."
        )

    except requests.RequestException as error:

        st.error(
            f"Request failed: {error}"
        )

    except ValueError:

        st.error(
            "The backend returned an "
            "invalid JSON response."
        )