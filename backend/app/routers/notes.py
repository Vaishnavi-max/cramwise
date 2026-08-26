from pathlib import Path
from typing import List
from uuid import uuid4
import json
import re

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.schemas.notes import (
    NotesDocumentResponse,
    NotesUploadResponse,
)

from app.services.upload_service import (
    UploadService,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/api/notes",
    tags=["Notes"],
)


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

NOTES_DIR = (
    BASE_DIR
    / "uploads"
    / "notes"
)


# ==========================================================
# SERVICE
# ==========================================================

upload_service = UploadService()


# ==========================================================
# NORMALIZATION
# ==========================================================

def normalize_subject(
    subject: str,
) -> str:
    """
    Normalize subject name.

    Example:

        " compiler   design "
                ↓
        "Compiler Design"
    """

    subject = " ".join(
        subject.strip().split()
    )

    if not subject:
        raise ValueError(
            "Subject cannot be empty."
        )

    return subject.title()


def normalize_course_code(
    course_code: str | None,
) -> str | None:
    """
    Normalize course code.

    Examples:

        "bcs 306" → "BCS306"
        "BCS 306" → "BCS306"
        "bcs306"  → "BCS306"
    """

    if course_code is None:
        return None

    normalized = "".join(
        course_code.strip().upper().split()
    )

    if not normalized:
        return None

    return normalized


def make_subject_folder(
    subject: str,
    course_code: str | None,
) -> str:
    """
    Create a safe folder name.

    Prefer course code because it is a
    stable subject identifier.

    Example:

        Compiler Design + BCS306
        → BCS306
    """

    if course_code:

        return re.sub(
            r"[^A-Z0-9_-]",
            "_",
            course_code,
        )

    folder = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        subject,
    )

    return folder.strip("_")


# ==========================================================
# NOTES UPLOAD API
# ==========================================================

@router.post(
    "/upload",
    response_model=NotesUploadResponse,
)
async def upload_notes(
    files: List[UploadFile] = File(
        ...,
        description=(
            "Select one or more Notes PDF files."
        ),
    ),

    subject: str = Form(
        ...,
        description="Subject name.",
    ),

    course_code: str | None = Form(
        None,
        description="Course code, e.g. BCS 306.",
    ),
):
    """
    Upload one or multiple Notes PDFs.

    All files in one request belong to the
    same subject/course.

    Each PDF receives its own document_id.

    Example:

        Module 1.pdf
        Module 2.pdf
        Module 3.pdf

    uploaded together as:

        subject = Compiler Design
        course_code = BCS 306

    Result:

        uploads/
            notes/
                BCS306/
                    NOTES_xxx/
                        Module 1.pdf
                        metadata.json

                    NOTES_yyy/
                        Module 2.pdf
                        metadata.json

                    NOTES_zzz/
                        Module 3.pdf
                        metadata.json
    """

    # ======================================================
    # STEP 1 — NORMALIZE SUBJECT
    # ======================================================

    try:

        normalized_subject = (
            normalize_subject(
                subject
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # ======================================================
    # STEP 2 — NORMALIZE COURSE CODE
    # ======================================================

    normalized_course_code = (
        normalize_course_code(
            course_code
        )
    )

    # ======================================================
    # STEP 3 — VALIDATE FILE LIST
    # ======================================================

    if not files:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one Notes PDF "
                "must be uploaded."
            ),
        )

    # ======================================================
    # STEP 4 — SUBJECT DIRECTORY
    # ======================================================

    subject_folder = (
        make_subject_folder(
            subject=normalized_subject,
            course_code=(
                normalized_course_code
            ),
        )
    )

    subject_dir = (
        NOTES_DIR
        / subject_folder
    )

    subject_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    uploaded_documents = []

    # ======================================================
    # STEP 5 — PROCESS EACH PDF
    # ======================================================

    for file in files:

        # --------------------------------------------------
        # 5.1 FILE NAME
        # --------------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Every uploaded file "
                    "must have a name."
                ),
            )

        filename = Path(
            file.filename
        ).name

        # --------------------------------------------------
        # 5.2 PDF EXTENSION
        # --------------------------------------------------

        if not filename.lower().endswith(
            ".pdf"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"'{filename}' is not a PDF. "
                    "Only PDF Notes files are supported."
                ),
            )

        # --------------------------------------------------
        # 5.3 CONTENT TYPE
        # --------------------------------------------------

        if (
            file.content_type
            and file.content_type
            != "application/pdf"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"'{filename}' does not have "
                    "application/pdf content type."
                ),
            )

        # --------------------------------------------------
        # 5.4 DOCUMENT ID
        # --------------------------------------------------

        document_id = (
            f"NOTES_{uuid4().hex}"
        )

        # --------------------------------------------------
        # 5.5 DOCUMENT DIRECTORY
        # --------------------------------------------------

        document_dir = (
            subject_dir
            / document_id
        )

        destination = (
            document_dir
            / filename
        )

        # --------------------------------------------------
        # 5.6 SAVE PDF
        # --------------------------------------------------

        try:

            saved_path = (
                upload_service.save_file(
                    file=file,
                    destination=destination,
                )
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to save "
                    f"'{filename}': {exc}"
                ),
            )

        # --------------------------------------------------
        # 5.7 CREATE METADATA
        # --------------------------------------------------

        metadata = {

            "document_id": document_id,

            "document_name": (
                saved_path.name
            ),

            "document_type": "NOTES",

            "subject": normalized_subject,

            "course_code": (
                normalized_course_code
            ),

            "subject_folder": subject_folder,

            "file_path": str(
                saved_path
            ),
        }

        metadata_path = (
            document_dir
            / "metadata.json"
        )

        # --------------------------------------------------
        # 5.8 SAVE METADATA
        # --------------------------------------------------

        try:

            metadata_path.write_text(
                json.dumps(
                    metadata,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        except Exception as exc:

            # Roll back PDF if metadata fails.

            try:

                saved_path.unlink(
                    missing_ok=True
                )

                document_dir.rmdir()

            except Exception:
                pass

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to save metadata "
                    f"for '{filename}': {exc}"
                ),
            )

        # --------------------------------------------------
        # 5.9 ADD RESPONSE
        # --------------------------------------------------

        uploaded_documents.append(
            NotesDocumentResponse(

                document_id=document_id,

                document_name=(
                    saved_path.name
                ),

                document_type="NOTES",

                subject=normalized_subject,

                course_code=(
                    normalized_course_code
                ),

                subject_folder=(
                    subject_folder
                ),
            )
        )

    # ======================================================
    # STEP 6 — FINAL RESPONSE
    # ======================================================

    return NotesUploadResponse(

        success=True,

        subject=normalized_subject,

        course_code=(
            normalized_course_code
        ),

        uploaded_count=len(
            uploaded_documents
        ),

        documents=uploaded_documents,

        message=(
            f"{len(uploaded_documents)} "
            "Notes file(s) uploaded successfully."
        ),
    )