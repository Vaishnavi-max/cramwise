class QuestionEnricher:
    """
    Adds academic metadata to already-parsed questions.

    This class does NOT:
    - call an LLM
    - modify question text
    - perform OCR
    - determine units using AI

    Marks and units are assigned using fixed examination rules.
    """

    # ==========================================================
    # MIDTERM MAPPING
    # ==========================================================

    MIDTERM_MAPPING = {
        (1, "a"): {"unit": 1, "marks": 2.5},
        (1, "b"): {"unit": 1, "marks": 2.5},
        (1, "c"): {"unit": 2, "marks": 2.5},
        (1, "d"): {"unit": 2, "marks": 2.5},

        (2, "a"): {"unit": 1, "marks": 5},
        (2, "b"): {"unit": 1, "marks": 5},
        (2, "c"): {"unit": 1, "marks": 5},

        (3, "a"): {"unit": 1, "marks": 5},
        (3, "b"): {"unit": 1, "marks": 5},
        (3, "c"): {"unit": 1, "marks": 5},
    }

    # ==========================================================
    # ENDTERM MAPPING
    # ==========================================================

    ENDTERM_MAPPING = {
        (1, "a"): {"unit": 1, "marks": 2.5},
        (1, "b"): {"unit": 1, "marks": 2.5},
        (1, "c"): {"unit": 2, "marks": 2.5},
        (1, "d"): {"unit": 2, "marks": 2.5},
        (1, "e"): {"unit": 3, "marks": 2.5},
        (1, "f"): {"unit": 3, "marks": 2.5},
        (1, "g"): {"unit": 4, "marks": 2.5},
        (1, "h"): {"unit": 4, "marks": 2.5},

        (2, ""): {"unit": 1, "marks": 10},
        (3, ""): {"unit": 1, "marks": 10},

        (4, ""): {"unit": 2, "marks": 10},
        (5, ""): {"unit": 2, "marks": 10},

        (6, ""): {"unit": 3, "marks": 10},
        (7, ""): {"unit": 3, "marks": 10},

        (8, ""): {"unit": 4, "marks": 10},
        (9, ""): {"unit": 4, "marks": 10},
    }

    # ==========================================================
    # NORMALIZE PART
    # ==========================================================

    @staticmethod
    def normalize_part(part):
        """
        Converts:

        a)
        A)
        a

        into:

        a
        """

        if part is None:
            return ""

        part = str(part).strip().lower()

        if part.endswith(")"):
            part = part[:-1]

        return part

    # ==========================================================
    # GET MAPPING
    # ==========================================================

    @classmethod
    def get_mapping(
        cls,
        exam_type,
        question_number,
        part,
    ):
        """
        Returns:

        {
            "unit": ...,
            "marks": ...
        }

        based on the fixed examination scheme.
        """

        exam_type = (
            exam_type or ""
        ).strip().upper()

        part = cls.normalize_part(part)

        try:
            question_number = int(
                question_number
            )
        except (TypeError, ValueError):
            return None

        if exam_type == "MIDTERM":

            mapping = cls.MIDTERM_MAPPING

        elif exam_type == "ENDTERM":

            mapping = cls.ENDTERM_MAPPING

        else:

            return None

        return mapping.get(
            (question_number, part)
        )