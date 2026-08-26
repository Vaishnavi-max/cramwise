from dataclasses import dataclass
import re


@dataclass
class PaperGroup:
    """
    Represents one complete examination paper.
    """

    subject: str
    subject_code: str
    exam_type: str
    semester: int | None
    pages: list[int]

    @property
    def paper_id(self) -> str:
        """
        Generate a safe identifier for the paper.

        Example:

        BCS 306 + ENDTERM
        ->
        BCS_306_ENDTERM

        HMC-306 + MIDTERM
        ->
        HMC_306_MIDTERM
        """

        # Normalize subject code
        safe_code = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            self.subject_code.strip(),
        )

        # Remove extra underscores
        safe_code = re.sub(
            r"_+",
            "_",
            safe_code,
        ).strip("_")

        # Normalize exam type
        safe_exam = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            self.exam_type.strip().upper(),
        )

        safe_exam = re.sub(
            r"_+",
            "_",
            safe_exam,
        ).strip("_")

        return f"{safe_code}_{safe_exam}"


class PaperGrouper:

    @staticmethod
    def group(
        page_metadata: list[tuple[int, dict]]
    ) -> list[PaperGroup]:
        """
        Groups pages into complete examination papers.

        Rule:

        A page with paper identity starts a new paper.

        A page without identity belongs to the
        previous paper.
        """

        papers = []

        current_paper = None

        for page_number, metadata in page_metadata:

            exam_type = metadata.get("exam_type")
            subject = metadata.get("subject")
            subject_code = metadata.get("subject_code")
            semester = metadata.get("semester")

            # ------------------------------------------------
            # NEW PAPER
            # ------------------------------------------------

            if (
                exam_type is not None
                and subject_code is not None
            ):

                current_paper = PaperGroup(
                    subject=subject or "",
                    subject_code=subject_code,
                    exam_type=exam_type,
                    semester=semester,
                    pages=[page_number],
                )

                papers.append(current_paper)

            # ------------------------------------------------
            # CONTINUATION PAGE
            # ------------------------------------------------

            else:

                if current_paper is not None:

                    current_paper.pages.append(
                        page_number
                    )

                else:

                    print(
                        f"WARNING: Page {page_number} "
                        f"has no paper identity and "
                        f"no previous paper exists."
                    )

        return papers