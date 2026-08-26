import json
from pathlib import Path

from app.services.question_enricher import QuestionEnricher


class QuestionEnrichmentService:

    def __init__(self):
        self.enricher = QuestionEnricher()

    def enrich_paper(
        self,
        question_file: Path,
        paper_metadata: dict,
        output_file: Path,
    ):
        """
        Enrich one paper's parsed questions.

        Reads M3.5 JSON.
        Applies deterministic M4 mapping.
        Saves a new enriched JSON.
        """

        questions = json.loads(
            question_file.read_text(
                encoding="utf-8"
            )
        )

        exam_type = (
            paper_metadata
            .get("exam_type", "")
            .strip()
            .upper()
        )

        enriched_questions = []

        for question in questions:

            question_number = question.get(
                "question_number"
            )

            part = question.get(
                "part",
                ""
            )

            # ------------------------------------------
            # Normalize question number
            # ------------------------------------------

            try:

                question_number = int(
                    question_number
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    f"Invalid question number: "
                    f"{question_number}"
                )

            # ------------------------------------------
            # Normalize part
            # ------------------------------------------

            normalized_part = (
                self.enricher.normalize_part(
                    part
                )
            )

            # ------------------------------------------
            # Get M4 mapping
            # ------------------------------------------

            mapping = (
                self.enricher.get_mapping(
                    exam_type=exam_type,
                    question_number=question_number,
                    part=normalized_part,
                )
            )

            # ==================================================
            # ENDTERM Q2-Q9
            # ==================================================
            #
            # These questions may have subparts.
            #
            # Example:
            #
            # Q2 a
            # Q2 b
            #
            # The paper rule still says:
            #
            # Q2 -> Unit 1 -> 10 marks
            #
            # So use the main-question mapping.
            # ==================================================

            if mapping is None:

                if (
                    exam_type == "ENDTERM"
                    and 2 <= question_number <= 9
                ):

                    mapping = (
                        self.enricher.get_mapping(
                            exam_type=exam_type,
                            question_number=question_number,
                            part="",
                        )
                    )

            # ------------------------------------------
            # Fail if no mapping exists
            # ------------------------------------------

            if mapping is None:

                raise ValueError(
                    f"No M4 mapping found for "
                    f"{exam_type} "
                    f"Q{question_number}"
                    f"{normalized_part}"
                )

            # ------------------------------------------
            # Build enriched question
            # ------------------------------------------

            enriched_question = {

                "paper_id": paper_metadata[
                    "paper_id"
                ],

                "subject": paper_metadata.get(
                    "subject"
                ),

                "subject_code": paper_metadata.get(
                    "subject_code"
                ),

                "exam_type": exam_type,

                "semester": paper_metadata.get(
                    "semester"
                ),

                "question_number": question_number,

                "sub_question": (
                    normalized_part
                    if normalized_part
                    else None
                ),

                "text": question.get(
                    "text",
                    ""
                ),

                "marks": mapping[
                    "marks"
                ],

                "unit": mapping[
                    "unit"
                ],

                "co": question.get(
                    "co"
                ),
            }

            enriched_questions.append(
                enriched_question
            )

        # ------------------------------------------
        # Save
        # ------------------------------------------

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            json.dumps(
                enriched_questions,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return enriched_questions