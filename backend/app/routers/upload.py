from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)

from app.services.upload_service import (
    UploadService,
)

from app.services.syllabus_pipeline_service import (
    SyllabusPipelineService,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


# ==========================================================
# SERVICES
# ==========================================================

upload_service = UploadService()

syllabus_pipeline = SyllabusPipelineService()


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

SYLLABUS_DIR = (
    BASE_DIR
    / "uploads"
    / "syllabus"
)

PYQ_DIR = (
    BASE_DIR
    / "uploads"
    / "pyqs"
)


# ==========================================================
# SYLLABUS UPLOAD
# ==========================================================

@router.post("/syllabus")
def upload_syllabus(
    file: UploadFile = File(...),
):
    """
    Upload and process a syllabus PDF.

    Complete flow:

        React
          ↓
        POST /upload/syllabus
          ↓
        Save original PDF
          ↓
        SyllabusPipelineService
          ↓
        OCRmyPDF + Tesseract
          ↓
        Searchable OCR PDF
          ↓
        SyllabusParser
          ↓
        Structured syllabus
          ↓
        JSON response
    """

    # ------------------------------------------------------
    # 1. Validate filename
    # ------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )

    filename = Path(
        file.filename
    ).name

    # ------------------------------------------------------
    # 2. Validate PDF
    # ------------------------------------------------------

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF syllabus files are supported.",
        )

    # ------------------------------------------------------
    # 3. Create destination
    # ------------------------------------------------------

    destination = (
        SYLLABUS_DIR
        / filename
    )

    # ------------------------------------------------------
    # 4. Save uploaded PDF
    # ------------------------------------------------------

    try:

        saved_path = upload_service.save_file(
            file=file,
            destination=destination,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save syllabus: {exc}"
            ),
        ) from exc

    # ------------------------------------------------------
    # 5. Run complete syllabus pipeline
    # ------------------------------------------------------

    try:

        result = syllabus_pipeline.process(
            saved_path
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Syllabus processing failed: "
                f"{exc}"
            ),
        ) from exc

    # ------------------------------------------------------
    # 6. Validate pipeline result
    # ------------------------------------------------------

    if not isinstance(result, list):

        raise HTTPException(
            status_code=500,
            detail=(
                "Syllabus pipeline returned "
                "an invalid result."
            ),
        )

    # ------------------------------------------------------
    # 7. Return processed result
    # ------------------------------------------------------

    return {
        "filename": filename,
        "status": "processed successfully",
        "course_count": len(result),
        "courses": result,
    }


# ==========================================================
# PYQ UPLOAD
# ==========================================================

@router.post("/pyq")
def upload_pyq(
    file: UploadFile = File(...),
):
    """
    Upload a PYQ PDF.

    Current flow:

        React
          ↓
        POST /upload/pyq
          ↓
        Validate PDF
          ↓
        Save PDF

    PYQ OCR/parsing is not connected here yet.
    """

    # ------------------------------------------------------
    # 1. Validate filename
    # ------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )

    filename = Path(
        file.filename
    ).name

    # ------------------------------------------------------
    # 2. Validate PDF
    # ------------------------------------------------------

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF PYQ files are supported.",
        )

    # ------------------------------------------------------
    # 3. Destination
    # ------------------------------------------------------

    destination = (
        PYQ_DIR
        / filename
    )

    # ------------------------------------------------------
    # 4. Save file
    # ------------------------------------------------------

    try:

        saved_path = upload_service.save_file(
            file=file,
            destination=destination,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save PYQ: {exc}"
            ),
        ) from exc

    # ------------------------------------------------------
    # 5. Current response
    # ------------------------------------------------------

    return {
        "filename": filename,
        "status": "uploaded successfully",
        "path": str(saved_path),
    }