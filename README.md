# CodeSentinel

AI-powered software debugging agent that investigates repository issues, generates code patches, executes tests in an isolated workspace, critiques the result, and retries when necessary.

## Overview

CodeSentinel is a defensive AI software-engineering agent built around a stateful LangGraph workflow.

Given a repository and a bug report, CodeSentinel:

1. Understands the issue.
2. Analyzes the repository structure.
3. Retrieves relevant code using semantic search.
4. Investigates the likely root cause.
5. Generates a minimal code patch.
6. Creates an isolated workspace.
7. Applies the patch.
8. Runs the repository's tests.
9. Uses a Critic Agent to evaluate the result.
10. Retries when the patch is rejected or tests fail.
11. Produces a final debugging/PR report.

The system is designed around evidence-driven debugging rather than trusting an LLM-generated patch without execution and validation.

## Architecture

```text
                    ┌──────────────────────┐
                    │      Bug Report      │
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
                        Test Runner
                               │
                         ┌─────┴─────┐
                         │           │
                       FAIL        PASS
                         │           │
                         ▼           ▼
                       Retry       Critic
                         │         ┌──┴──┐
                         │         │     │
                         │      REJECT APPROVE
                         │         │     │
                         └────►    Retry Report
                                      │
                                      ▼
                                     END
```

## LangGraph Workflow

The workflow is modeled as a stateful, cyclical graph.

```text
START
  ↓
Issue Understanding
  ↓
Repository Analysis
  ↓
Retrieval
  ↓
Investigation
  ↓
Patch Generation
  ↓
Workspace
  ↓
Test Runner
  ├── tests fail → Retry → Patch Generation
  │
  └── tests pass → Critic
                    ├── reject → Retry
                    └── approve → Report → END
```

A maximum retry count prevents infinite loops.

## Key Components

### Issue Understanding Agent

Converts the natural-language bug report into a structured `IssueTask`.

### Repository Analyzer

Uses Python AST analysis to build a `RepoMap` containing files, modules, dependencies, functions, and classes.

### Semantic Retrieval

Uses `SentenceTransformer` embeddings with FAISS similarity search to retrieve relevant code chunks.

The embedding model is cached and reused across retrieval instances to avoid repeated model loading.

### Investigation Agent

Combines the repository map and retrieved code to produce a structured `Hypothesis` containing:

* root-cause explanation
* confidence score
* suspected files

### Patch Generator

Generates a structured `Patch` containing the target file and proposed code diff.

### Isolated Workspace

Copies the repository into a temporary workspace before applying a generated patch. This prevents the original repository from being modified during experimentation.

### Test Runner

Runs the repository's pytest suite inside the temporary workspace and records:

* pass/fail status
* logs
* coverage delta placeholder

### Critic Agent

Evaluates the generated patch using the hypothesis, patch, test result, and relevant test behavior.

The Critic can:

* approve the patch
* reject the patch
* request a retry

### PR Report

Produces a human-readable report containing the root cause, confidence, changed file, test results, and critic reasoning.

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
* FastAPI
* Streamlit
* Git / GitHub

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

## Installation

Clone the repository and create a virtual environment:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CodeSentinel

python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

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

## FastAPI Backend

Start the API:

```powershell
python -m uvicorn backend.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

The main endpoint accepts:

```json
{
  "repo_path": "eval/demo_repos/basic_bug",
  "issue": "The application crashes when the discount value is set to None.",
  "max_retries": 3
}
```

## Streamlit Frontend

Start the dashboard in a second terminal:

```powershell
python -m streamlit run frontend/app.py
```

Then open the URL shown by Streamlit, typically:

```text
http://localhost:8501
```

The dashboard displays:

* investigation confidence
* suspected root cause
* changed file
* generated patch
* test results and logs
* critic verdict
* retry count
* final PR report

## Evaluation

CodeSentinel was tested against five intentionally buggy demo repositories:

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
Average execution time: 20.33s
```

The evaluation is a controlled five-scenario benchmark and should not be interpreted as production-level reliability.

## Testing

Run the complete automated test suite:

```powershell
pytest
```

Current project test coverage includes:

* repository analysis
* code chunking
* semantic retrieval
* issue understanding
* investigation
* patch generation
* patch application
* isolated workspaces
* test execution
* critic decisions
* retry routing
* full LangGraph retry flow

The latest full suite contains **30 passing tests**.

## Example

Given the bug:

```text
The application crashes when the discount value is set to None.
```

CodeSentinel can identify the root cause:

```python
def get_final_price(price, discount):
    if discount is None:
        return calculate_discount(price, discount)
```

Generate a patch:

```diff
 def get_final_price(price, discount):
     if discount is None:
-        return calculate_discount(price, discount)
+        return price
```

Run the repository tests:

```text
2 passed
```

Then the Critic approves the patch and the system generates a final report.

## Safety and Design Principles

CodeSentinel is designed to reduce the risk of blindly applying AI-generated changes.

The workflow:

* works in a temporary workspace rather than directly modifying the original repository
* validates changes with actual tests
* uses a retry limit
* uses a separate Critic step before accepting a successful patch
* keeps structured state and contracts between components

## Current Limitations

The current implementation is an MVP and has several known limitations:

* evaluation uses a small controlled set of five demo repositories
* the Test Runner currently relies on pytest
* temporary workspaces are currently managed locally
* LLM-backed tests can be slower and dependent on network/API availability
* evaluation currently measures test success and execution time, but not a large benchmark of real-world repositories
* the current API stores run results in memory rather than a persistent database
* authentication and multi-user access control are not implemented

## Future Improvements

Potential next steps include:

* Docker-based sandbox execution
* persistent run storage
* GitHub repository integration
* automatic pull-request creation
* richer regression testing
* larger evaluation benchmarks
* mocked LLM tests for faster CI
* asynchronous backend jobs
* authentication and access control
* improved patch validation
* better retry feedback using previous test failures and critic feedback

## Author

Built as an AI software-engineering project demonstrating:

* agentic workflows
* LangGraph state management
* semantic code retrieval
* LLM-based debugging
* automated patch generation
* test-driven validation
* self-correcting retry loops
* FastAPI backend development
* Streamlit application development
