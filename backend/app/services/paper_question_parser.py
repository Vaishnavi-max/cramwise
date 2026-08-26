from app.parsers.question_parser import QuestionParser
from app.services.paper_text_builder import PaperTextBuilder


class PaperQuestionParser:
    """
    Parses questions for one complete examination paper.

    Flow:

    paper pages
        ↓
    PaperTextBuilder
        ↓
    combined OCR
        ↓
    QuestionParser
        ↓
    validated questions
    """

    def __init__(self):

        self.text_builder = PaperTextBuilder()

        self.question_parser = QuestionParser()

    def parse(
        self,
        document_name: str,
        paper_id: str,
        pages: list[int],
    ):
        """
        Parse one complete paper.

        Example:

        document_name:
            6thsempyqs_2025

        paper_id:
            BCS_306_ENDTERM

        pages:
            [3, 4]
        """

        # ======================================================
        # STEP 1
        # ======================================================

        combined_text = (
            self.text_builder.build(
                document_name=document_name,
                pages=pages,
            )
        )

        # ======================================================
        # STEP 2
        # ======================================================

        questions = (
            self.question_parser.get_questions(
                paper_id=paper_id,
                paper_text=combined_text,
                document_name=document_name,
            )
        )

        return questions