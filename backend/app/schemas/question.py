from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    question_number: int

    sub_question: str = ""

    raw_text: str = ""

    text: str = ""

    marks: Optional[float] = None

    total_marks: Optional[float] = None

    instruction: str = ""

    co: str = ""

    unit: str = ""