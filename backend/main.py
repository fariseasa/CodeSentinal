import shutil
import tempfile
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent.graph.graph import build_graph


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="CodeSentinel API",
    description="AI-powered software debugging agent",
    version="0.2.0",
)


# ============================================================
# RUN STORAGE
# ============================================================

runs = {}


# ============================================================
# UPLOAD SECURITY LIMITS
# ============================================================

# Maximum compressed ZIP size
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# Maximum total uncompressed ZIP size
MAX_EXTRACTED_SIZE = 200 * 1024 * 1024  # 200 MB

# Maximum number of files/directories inside ZIP
MAX_FILE_COUNT = 2000


# ============================================================
# PATCHED REPOSITORY STORAGE
# ============================================================

PATCHED_REPOS_DIR = (
    Path(tempfile.gettempdir())
    / "codesentinel_patched_repos"
)

PATCHED_REPOS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# RESPONSE MODELS
# ============================================================

class RunResponse(BaseModel):
    run_id: str
    status: str


class RunResult(BaseModel):
    run_id: str
    status: str
    issue: str

    root_cause: str | None = None
    confidence: float | None = None

    changed_file: str | None = None
    patch: str | None = None

    tests_passed: bool | None = None
    test_logs: str | None = None

    critic_approved: bool | None = None
    critic_reasoning: str | None = None

    retry_count: int = 0
    retry_history: list[dict] = []

    report: str | None = None

    patched_zip_available: bool = False


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "service": "CodeSentinel",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "codesentinel",
    }


# ============================================================
# SAFE ZIP EXTRACTION
# ============================================================

def extract_zip_safely(
    zip_path: Path,
    destination: Path,
) -> Path:
    """
    Extract a ZIP safely.

    Protections:
    - Path traversal prevention
    - Absolute path prevention
    - Maximum file count
    - Maximum extracted size

    Returns the repository root to analyze.
    """

    with ZipFile(zip_path, "r") as archive:

        members = archive.infolist()

        # ----------------------------------------------------
        # Empty ZIP
        # ----------------------------------------------------

        if not members:
            raise ValueError(
                "ZIP file is empty."
            )

        # ----------------------------------------------------
        # File count limit
        # ----------------------------------------------------

        if len(members) > MAX_FILE_COUNT:
            raise ValueError(
                "ZIP contains too many files. "
                f"Maximum allowed is {MAX_FILE_COUNT}."
            )

        destination = destination.resolve()

        total_uncompressed_size = 0

        # ----------------------------------------------------
        # Validate every ZIP entry
        # ----------------------------------------------------

        for member in members:

            member_path = (
                destination / member.filename
            ).resolve()

            # Prevent path traversal
            try:

                member_path.relative_to(
                    destination
                )

            except ValueError as error:

                raise ValueError(
                    "ZIP contains an unsafe path."
                ) from error

            # ------------------------------------------------
            # Track extracted size
            # ------------------------------------------------

            total_uncompressed_size += (
                member.file_size
            )

            if (
                total_uncompressed_size
                > MAX_EXTRACTED_SIZE
            ):

                raise ValueError(
                    "ZIP contents exceed the "
                    "200 MB extracted size limit."
                )

        # ----------------------------------------------------
        # Extract only after validation
        # ----------------------------------------------------

        archive.extractall(
            destination
        )

    # ========================================================
    # DETERMINE REPOSITORY ROOT
    # ========================================================

    entries = list(
        destination.iterdir()
    )

    # Case 1:
    #
    # project.zip
    # ├── app.py
    # └── tests/
    #

    # Case 2:
    #
    # project.zip
    # └── project/
    #     ├── app.py
    #     └── tests/
    #

    if (
        len(entries) == 1
        and entries[0].is_dir()
    ):
        return entries[0]

    return destination


# ============================================================
# SAVE UPLOADED ZIP
# ============================================================

def save_upload(
    upload: UploadFile,
    destination: Path,
):
    """
    Save uploaded ZIP while enforcing the
    maximum compressed upload size.
    """

    total_size = 0

    with destination.open("wb") as output:

        while True:

            chunk = upload.file.read(
                1024 * 1024
            )

            if not chunk:
                break

            total_size += len(chunk)

            # ------------------------------------------------
            # Maximum upload size
            # ------------------------------------------------

            if total_size > MAX_UPLOAD_SIZE:

                raise ValueError(
                    "Uploaded ZIP exceeds "
                    "the 50 MB limit."
                )

            output.write(chunk)


# ============================================================
# CREATE PATCHED REPOSITORY ZIP
# ============================================================

def create_patched_zip(
    repo_path: Path,
    run_id: str,
) -> Path:
    """
    Create a ZIP containing the final patched repository.
    """

    output_base = (
        PATCHED_REPOS_DIR
        / f"codesentinel_{run_id}"
    )

    archive_path = Path(
        shutil.make_archive(
            str(output_base),
            "zip",
            root_dir=repo_path,
        )
    )

    return archive_path


# ============================================================
# CREATE RUN
# ============================================================

@app.post(
    "/run",
    response_model=RunResponse,
)
def create_run(
    repo_zip: UploadFile = File(...),
    issue: str = Form(...),
    max_retries: int = Form(3),
):

    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not repo_zip.filename:

        raise HTTPException(
            status_code=400,
            detail="A ZIP file is required.",
        )

    if not repo_zip.filename.lower().endswith(
        ".zip"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only .zip repository uploads "
                "are supported."
            ),
        )

    # ========================================================
    # VALIDATE ISSUE
    # ========================================================

    if not issue.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug report is required.",
        )

    # ========================================================
    # VALIDATE RETRIES
    # ========================================================

    if (
        max_retries < 0
        or max_retries > 5
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "max_retries must be "
                "between 0 and 5."
            ),
        )

    # ========================================================
    # CREATE RUN ID
    # ========================================================

    run_id = str(
        uuid4()
    )

    runs[run_id] = {
        "status": "running",
        "issue": issue,
        "result": None,
        "patched_zip": None,
    }

    # ========================================================
    # TEMPORARY WORKSPACE
    # ========================================================

    temp_root = Path(
        tempfile.mkdtemp(
            prefix="codesentinel_upload_"
        )
    )

    zip_path = (
        temp_root / "repository.zip"
    )

    try:

        # ====================================================
        # SAVE ZIP
        # ====================================================

        try:

            save_upload(
                repo_zip,
                zip_path,
            )

        except ValueError as error:

            runs[run_id]["status"] = (
                "failed"
            )

            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        # ====================================================
        # CREATE EXTRACTION DIRECTORY
        # ====================================================

        extracted_root = (
            temp_root / "repository"
        )

        extracted_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ====================================================
        # EXTRACT ZIP
        # ====================================================

        try:

            repo_path = extract_zip_safely(
                zip_path,
                extracted_root,
            )

        except (
            BadZipFile,
            ValueError,
        ) as error:

            runs[run_id]["status"] = (
                "failed"
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid repository ZIP: "
                    f"{error}"
                ),
            ) from error

        # ====================================================
        # BUILD LANGGRAPH WORKFLOW
        # ====================================================

        graph = build_graph()

        # ====================================================
        # RUN CODE SENTINEL
        # ====================================================

        result = graph.invoke(
            {
                "repo_path": str(
                    repo_path
                ),
                "issue": issue,
                "retry_count": 0,
                "max_retries": max_retries,
            }
        )

        # ====================================================
        # CREATE PATCHED ZIP
        # ====================================================

        patched_zip_path = None

        if repo_path.exists():

            patched_zip_path = (
                create_patched_zip(
                    repo_path,
                    run_id,
                )
            )

            runs[run_id]["patched_zip"] = (
                str(patched_zip_path)
            )

        # ====================================================
        # EXTRACT RESULTS
        # ====================================================

        hypothesis = result.get(
            "hypothesis"
        )

        patch = result.get(
            "patch"
        )

        test_result = result.get(
            "test_result"
        )

        critic = result.get(
            "critic_verdict"
        )

        # ====================================================
        # CLEAN RESULT FOR API
        # ====================================================

        clean_result = {
            "run_id": run_id,
            "status": "completed",
            "issue": issue,

            "root_cause": (
                hypothesis.explanation
                if hypothesis
                else None
            ),

            "confidence": (
                hypothesis.confidence
                if hypothesis
                else None
            ),

            "changed_file": (
                patch.file_path
                if patch
                else None
            ),

            "patch": (
                patch.diff
                if patch
                else None
            ),

            "tests_passed": (
                test_result.passed
                if test_result
                else None
            ),

            "test_logs": (
                test_result.logs
                if test_result
                else None
            ),

            "critic_approved": (
                critic.approved
                if critic
                else None
            ),

            "critic_reasoning": (
                critic.reasoning
                if critic
                else None
            ),

           "retry_history": result.get(
                "retry_history",
                [],
            ),

            "report": result.get(
                "report"
            ),

            "patched_zip_available": (
                patched_zip_path
                is not None
            ),
        }

        # ====================================================
        # SAVE RESULT
        # ====================================================

        runs[run_id]["status"] = (
            "completed"
        )

        runs[run_id]["result"] = (
            clean_result
        )

    # ========================================================
    # HTTP EXCEPTION
    # ========================================================

    except HTTPException:

        runs[run_id]["status"] = (
            "failed"
        )

        raise

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as error:

        runs[run_id]["status"] = (
            "failed"
        )

        runs[run_id]["result"] = {
            "run_id": run_id,
            "status": "failed",
            "issue": issue,
            "error": str(error),
        }

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    # ========================================================
    # ALWAYS CLEAN TEMPORARY WORKSPACE
    # ========================================================

    finally:

        shutil.rmtree(
            temp_root,
            ignore_errors=True,
        )

    # ========================================================
    # RETURN RUN ID
    # ========================================================

    return RunResponse(
        run_id=run_id,
        status="completed",
    )


# ============================================================
# GET RUN RESULT
# ============================================================

@app.get(
    "/run/{run_id}",
    response_model=RunResult,
)
def get_run(
    run_id: str,
):

    run = runs.get(
        run_id
    )

    # ========================================================
    # RUN NOT FOUND
    # ========================================================

    if run is None:

        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    # ========================================================
    # STILL RUNNING
    # ========================================================

    if run["result"] is None:

        raise HTTPException(
            status_code=202,
            detail=(
                "Run is still in progress."
            ),
        )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return run["result"]


# ============================================================
# DOWNLOAD PATCHED REPOSITORY
# ============================================================

@app.get(
    "/run/{run_id}/download",
)
def download_patched_repository(
    run_id: str,
):

    # ========================================================
    # FIND RUN
    # ========================================================

    run = runs.get(
        run_id
    )

    if run is None:

        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    # ========================================================
    # FIND PATCHED ZIP
    # ========================================================

    patched_zip = run.get(
        "patched_zip"
    )

    if not patched_zip:

        raise HTTPException(
            status_code=404,
            detail=(
                "No patched repository "
                "is available for this run."
            ),
        )

    patched_zip_path = Path(
        patched_zip
    )

    # ========================================================
    # CHECK FILE EXISTS
    # ========================================================

    if not patched_zip_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Patched repository ZIP "
                "is no longer available."
            ),
        )

    # ========================================================
    # RETURN ZIP
    # ========================================================

    return FileResponse(
        path=patched_zip_path,
        media_type="application/zip",
        filename=(
            f"codesentinel_fixed_"
            f"{run_id}.zip"
        ),
    )