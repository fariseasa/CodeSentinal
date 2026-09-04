# CodeSentinel

AI-powered software debugging agent that investigates repository issues, generates code patches, executes tests in an isolated Docker environment, critiques the result, retries when necessary, and produces a final debugging report.

## Overview

CodeSentinel is a defensive AI software-engineering agent built around a stateful, cyclical LangGraph workflow.

A user can upload a Python repository as a ZIP file and provide a natural-language bug report. CodeSentinel then:

1. Understands the reported issue.
2. Analyzes the repository structure.
3. Retrieves relevant code using semantic search.
4. Investigates the likely root cause.
5. Generates a minimal code patch.
6. Creates a temporary isolated workspace.
7. Applies the generated patch.
8. Builds a temporary Docker test environment.
9. Installs repository dependencies from `requirements.txt` when available.
10. Runs the repository's pytest suite inside Docker with network access disabled.
11. Uses a separate Critic Agent to evaluate the proposed fix.
12. Retries when tests fail or the Critic rejects the patch.
13. Produces a final debugging/PR report.
14. Creates a downloadable ZIP containing the patched repository.

The system is designed around evidence-driven debugging rather than trusting an LLM-generated patch without execution and validation.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │     Bug Report       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         Issue Understanding
                                    │
                                    ▼
                         Repository Analyzer
                                    │
                                    ▼
                        Semantic Code Retrieval
                                    │
                                    ▼
                          Investigation Agent
                                    │
                                    ▼
                           Patch Generator
                                    │
                                    ▼
                         Isolated Workspace
                                    │
                                    ▼
                           Patch Applier
                                    │
                                    ▼
                         Docker Test Runner
                                    │
                           ┌────────┴────────┐
                           │                 │
                         FAIL              PASS
                           │                 │
                           ▼                 ▼
                         Retry             Critic
                           │             ┌────┴────┐
                           │             │         │
                           │          REJECT    APPROVE
                           │             │         │
                           └──────► Retry│         ▼
                                         │       Report
                                         │         │
                                         └────►   END
```

---

## LangGraph Workflow

The debugging process is modeled as a stateful, cyclical LangGraph workflow.

```text
START
  ↓
Issue Understanding
  ↓
Repository Analysis
  ↓
Semantic Retrieval
  ↓
Investigation
  ↓
Patch Generation
  ↓
Workspace Creation
  ↓
Patch Application
  ↓
Docker Test Runner
  ├── Tests fail ──→ Retry ──→ Patch Generation
  │
  └── Tests pass ──→ Critic
                       ├── Reject ──→ Retry
                       │
                       └── Approve ──→ Report
                                         ↓
                                        END
```

A configurable retry limit prevents infinite correction loops.

---

## Key Components

### Issue Understanding Agent

Converts the natural-language bug report into a structured `IssueTask`.

### Repository Analyzer

Uses Python AST analysis to build a structured `RepoMap` containing repository files, modules, functions, classes, and dependencies.

### Semantic Retrieval

Uses Sentence Transformer embeddings with FAISS similarity search to retrieve relevant code chunks for the reported issue.

The embedding model is cached and reused across retrieval instances to avoid unnecessary repeated model loading.

### Investigation Agent

Combines the repository map and retrieved code to produce a structured `Hypothesis` containing:

* Root-cause explanation
* Confidence score
* Suspected files

### Patch Generator

Generates a structured `Patch` containing the target file and proposed code diff.

### Isolated Workspace

Copies the repository into a temporary workspace before applying generated changes. The original uploaded repository is not modified directly during experimentation.

### Docker Test Runner

The patched workspace is executed inside a temporary Docker image.

The runner:

* Uses Python 3.10
* Installs `pytest`
* Detects `requirements.txt`
* Installs declared project dependencies during Docker image creation
* Runs tests inside the container
* Disables network access during test execution
* Captures stdout and stderr
* Reports pass/fail status and test logs

### Critic Agent

Evaluates the proposed patch using the investigation hypothesis, generated patch, test results, and relevant test behavior.

The Critic can:

* Approve the patch
* Reject the patch
* Trigger another retry

### FastAPI Backend

Provides the API layer for:

* Repository ZIP uploads
* Bug reports
* Retry configuration
* Run results
* Patched repository downloads
* Health checks

### Streamlit Frontend

Provides the user interface for:

* Uploading repositories
* Entering bug reports
* Selecting maximum retries
* Viewing root-cause analysis
* Viewing generated patches
* Viewing test logs
* Viewing Critic decisions
* Downloading the patched repository

### PR Report

Produces a human-readable report containing:

* Root cause
* Confidence
* Changed file
* Generated patch
* Test results
* Critic verdict
* Critic reasoning

---

## Tech Stack

* Python
* LangGraph
* LangChain-compatible components
* Groq API
* OpenAI GPT-OSS-120B through Groq
* Sentence Transformers
* FAISS
* Pydantic
* Pytest
* Docker
* FastAPI
* Streamlit
* Git / GitHub

---

## Project Structure

```text
CodeSentinel/
│
├── agent/
│   ├── analyzer/
│   ├── critic/
│   ├── graph/
│   ├── investigation/
│   ├── issue/
│   ├── patch/
│   └── retrieval/
│
├── backend/
│   └── main.py
│
├── execution/
│   ├── patch_applier.py
│   ├── test_runner.py
│   └── workspace.py
│
├── eval/
│   ├── demo_repos/
│   │   ├── basic_bug/
│   │   ├── failing_test/
│   │   ├── api_bug/
│   │   ├── regression_bug/
│   │   └── refactor_bug/
│   │
│   ├── results/
│   │   └── evaluation_results.json
│   │
│   └── run_evaluation.py
│
├── frontend/
│   └── app.py
│
├── shared/
│   └── schemas.py
│
└── tests/
```

---

## Installation

### 1. Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CodeSentinel
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

Windows:

```powershell
.venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure the Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep the real API key private and never commit `.env` to Git.

---

## Docker Requirement

CodeSentinel uses Docker to execute repository tests inside an isolated environment.

Install and start Docker Desktop before using the Docker-based test runner.

Verify Docker:

```powershell
docker --version
```

Verify that the Docker engine is running:

```powershell
docker run --rm hello-world
```

---

## Running CodeSentinel

### Run the LangGraph workflow directly

```powershell
python -m experiments.test_full_graph
```

### Run the evaluation suite

```powershell
python -m eval.run_evaluation
```

Evaluation results are saved to:

```text
eval/results/evaluation_results.json
```

---

## FastAPI Backend

Start the backend:

```powershell
python -m uvicorn backend.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

### Main API endpoints

```text
POST /run
GET  /run/{run_id}
GET  /run/{run_id}/download
GET  /health
```

`POST /run` accepts:

* Repository ZIP
* Bug report
* Maximum retry count

The backend safely extracts the uploaded repository and passes it to the LangGraph workflow.

---

## Streamlit Frontend

Start the dashboard in a second terminal:

```powershell
python -m streamlit run frontend/app.py
```

Open:

```text
http://localhost:8501
```

The dashboard allows users to:

1. Upload a Python repository as a ZIP.
2. Enter a bug report.
3. Configure the maximum number of retries.
4. Start the debugging workflow.
5. View the root cause.
6. View the changed file.
7. View the generated patch.
8. View test results and logs.
9. View the Critic verdict.
10. View the final PR report.
11. Download the patched repository as a ZIP.

---

## Repository Upload

CodeSentinel accepts Python repositories as ZIP files.

The backend performs several security checks before extraction.

Current limits:

```text
Maximum ZIP upload size:       50 MB
Maximum extracted size:       200 MB
Maximum ZIP entries:         2,000
```

ZIP paths are validated to prevent path traversal before extraction.

Both of these layouts are supported:

```text
project.zip
├── app.py
├── calculator.py
└── tests/
```

and:

```text
project.zip
└── project/
    ├── app.py
    ├── calculator.py
    └── tests/
```

---

## Dependency Handling

When the uploaded repository contains:

```text
requirements.txt
```

CodeSentinel creates a temporary Docker image and installs those dependencies during image construction.

Example:

```text
requirements.txt
        ↓
Temporary Docker image
        ↓
pip install -r requirements.txt
        ↓
Run pytest
```

If `requirements.txt` is not present, the test environment still installs `pytest`.

Test execution itself is performed with Docker network access disabled.

---

## Example Workflow

Suppose a repository contains:

```python
def calculate_total(price, quantity):
    return price + quantity
```

and the bug report says:

```text
The calculate_total function produces an incorrect
result for price and quantity.
```

CodeSentinel can identify that:

```python
return price + quantity
```

is incorrectly adding the values.

It can generate a patch such as:

```diff
*** Begin Patch
*** Update File: calculator.py
@@
 def calculate_total(price, quantity):
-    return price + quantity
+    return price * quantity
*** End Patch
```

The patched repository is then tested inside Docker.

Example test output:

```text
============================= test session starts ==============================
platform linux -- Python 3.10.21
rootdir: /workspace

collected 1 item

tests/test_calculator.py . [100%]

============================== 1 passed in 0.02s ===============================
```

After successful validation, the Critic can approve the patch and CodeSentinel generates the final report.

The user can also download the complete patched repository as a ZIP file.

---

## Evaluation

CodeSentinel was evaluated against five intentionally buggy demo repositories:

| Scenario         | Bug Category                 | Result |
| ---------------- | ---------------------------- | ------ |
| `basic_bug`      | `None` / type handling       | PASS   |
| `failing_test`   | Incorrect arithmetic         | PASS   |
| `api_bug`        | Incorrect API response value | PASS   |
| `regression_bug` | Formatting regression        | PASS   |
| `refactor_bug`   | Empty-input edge case        | PASS   |

Current controlled evaluation:

```text
Total scenarios: 5
Passed: 5
Failed: 0
Success rate: 100%
```

The five-scenario evaluation is a controlled demonstration benchmark and should not be interpreted as production-level reliability.

---

## Testing

Run the complete automated test suite:

```powershell
pytest -q
```

Current suite status:

```text
32 passed
0 warnings
```

The test suite covers major components including:

* Repository analysis
* Code chunking
* Semantic retrieval
* Issue understanding
* Investigation
* Patch generation
* Patch application
* Workspace creation
* Docker test execution
* Dependency-aware Docker execution
* Critic decisions
* Retry routing
* Full LangGraph workflow

---

## Safety and Design Principles

CodeSentinel is designed to reduce the risk of blindly applying AI-generated changes.

The system:

* Works on a temporary workspace instead of directly modifying the original repository.
* Validates uploaded ZIP paths before extraction.
* Limits ZIP size, extracted size, and file count.
* Executes repository tests inside Docker.
* Disables network access during test execution.
* Validates generated changes using actual tests.
* Uses a separate Critic step before accepting a successful patch.
* Limits the number of retries.
* Uses structured Pydantic contracts between major components.
* Produces a final report describing the proposed change and validation results.

---

## Current Limitations

CodeSentinel is an MVP and has several limitations:

* Evaluation currently uses a small controlled set of five demo repositories.
* The test runner currently targets pytest-based Python repositories.
* Dependency detection currently focuses on `requirements.txt`.
* Temporary workspaces and run results are managed locally.
* Run state is currently stored in memory rather than a persistent database.
* LLM-backed execution depends on API availability and network connectivity during the AI stages.
* Evaluation does not yet represent a large real-world repository benchmark.
* Authentication and multi-user access control are not implemented.
* The API is currently designed for local/self-hosted usage.

---

## Future Improvements

Potential future improvements include:

* Support for `pyproject.toml`, Poetry, and other dependency formats.
* Persistent run storage.
* GitHub repository integration.
* Automatic pull-request creation.
* Larger real-world evaluation benchmarks.
* Mocked LLM tests for faster CI.
* Asynchronous backend jobs.
* Authentication and access control.
* Improved patch validation.
* Richer regression testing.
* More detailed retry feedback based on previous test failures and Critic reasoning.
* Support for additional programming languages and test frameworks.
* Better sandbox isolation and resource controls.

---

## Project Status

CodeSentinel currently provides an end-to-end local workflow:

```text
Repository ZIP
      ↓
Secure extraction
      ↓
Issue understanding
      ↓
Repository analysis
      ↓
Semantic retrieval
      ↓
Root-cause investigation
      ↓
Patch generation
      ↓
Patch application
      ↓
Docker dependency installation
      ↓
Docker test execution
      ↓
Critic validation
      ↓
Retry when required
      ↓
Final PR report
      ↓
Download patched repository
```

Current automated test status:

```text
32 passed
0 warnings
```

---

## Author

Built as an AI software-engineering project demonstrating:

* Agentic workflows
* LangGraph state management
* Semantic code retrieval
* LLM-based debugging
* Automated patch generation
* Test-driven validation
* Docker-based isolated execution
* Self-correcting retry loops
* FastAPI backend development
* Streamlit application development
* Defensive software-engineering practices
