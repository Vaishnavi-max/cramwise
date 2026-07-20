from pathlib import Path

from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

upload_service = UploadService()


@router.post("/syllabus")
def upload_syllabus(file: UploadFile = File(...)):

    destination = Path("uploads/syllabus") / file.filename

    upload_service.save_file(file, destination)

    return {
        "filename": file.filename,
        "status": "uploaded successfully"
    }