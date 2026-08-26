from dataclasses import dataclass, field

from app.schemas.question import Question


@dataclass
class Paper:

    subject: str

    subject_code: str

    semester: int

    exam_type: str

    duration: str

    maximum_marks: int

    questions: list[Question] = field(default_factory=list)