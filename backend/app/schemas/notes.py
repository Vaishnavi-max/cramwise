from pydantic import BaseModel


class NotesDocumentResponse(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    subject: str
    course_code: str | None
    subject_folder: str


class NotesUploadResponse(BaseModel):
    success: bool
    subject: str
    course_code: str | None
    uploaded_count: int
    documents: list[NotesDocumentResponse]
    message: str