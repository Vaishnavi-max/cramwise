import re


class ExamTypeClassifier:

    @staticmethod
    def classify(text: str) -> str | None:
        """
        Classify a page based on explicit exam-type keywords.

        Returns:
            "MIDTERM"
            "ENDTERM"
            None
        """

        if not text:
            return None

        text = text.upper()

        # Mid-term patterns
        midterm_patterns = [
            r"\bMID[\s-]*TERM\b",
            r"\bMID[\s-]*SEMESTER\b",
        ]

        # End-term patterns
        endterm_patterns = [
            r"\bEND[\s-]*TERM\b",
            r"\bEND[\s-]*SEMESTER\b",
        ]

        for pattern in midterm_patterns:
            if re.search(pattern, text):
                return "MIDTERM"

        for pattern in endterm_patterns:
            if re.search(pattern, text):
                return "ENDTERM"

        return None