from pydantic import BaseModel


class SyllabusCandidate(BaseModel):
    index_id: str
    course_code: str
    course_name: str
    unit_number: int
    topic: str
    subtopic: str | None
    search_text: str
    distance: float