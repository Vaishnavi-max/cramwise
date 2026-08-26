from collections import Counter


class QuestionOutputValidator:

    @staticmethod
    def validate(
        questions,
        exam_type: str,
    ) -> dict:
        """
        Validates already-saved parsed question JSON.

        Does NOT call the LLM.
        Does NOT modify the questions.
        """

        errors = []
        warnings = []

        exam_type = (
            exam_type or ""
        ).strip().upper()

        # ==================================================
        # 1. DETERMINE EXPECTED MAIN QUESTIONS
        # ==================================================

        if exam_type == "MIDTERM":

            expected_main_questions = {
                1,
                2,
                3,
            }

            required_q1_parts = {
                "a",
                "b",
                "c",
                "d",
            }

        elif exam_type == "ENDTERM":

            expected_main_questions = {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
            }

            required_q1_parts = {
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
            }

        else:

            errors.append(
                f"Unknown exam type: {exam_type}"
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
            }

        # ==================================================
        # 2. CHECK EMPTY OUTPUT
        # ==================================================

        if not questions:

            errors.append(
                "No questions were parsed."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
            }

        # ==================================================
        # 3. CHECK EACH QUESTION OBJECT
        # ==================================================

        identities = []
        question_numbers = []

        for index, question in enumerate(
            questions,
            start=1,
        ):

            # ------------------------------------------
            # Make sure object is a dictionary
            # ------------------------------------------

            if not isinstance(question, dict):

                errors.append(
                    f"Question object {index} "
                    f"is not a JSON object."
                )

                continue

            # ------------------------------------------
            # Extract fields
            # ------------------------------------------

            question_number = question.get(
                "question_number"
            )

            sub_question = question.get(
                "part",
                "",
            )

            text = question.get(
                "text",
                "",
            )

            # ------------------------------------------
            # Missing question number
            # ------------------------------------------

            if (
                question_number is None
                or str(question_number).strip() == ""
            ):

                errors.append(
                    f"Question object {index} "
                    f"has no question number."
                )

                continue

            # ------------------------------------------
            # Validate question number
            # ------------------------------------------

            try:

                question_number = int(
                    question_number
                )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    f"Invalid question number "
                    f"'{question_number}' "
                    f"at object {index}."
                )

                continue

            question_numbers.append(
                question_number
            )

            # ------------------------------------------
            # Normalize sub-question
            # ------------------------------------------

            sub_question = (
                str(sub_question or "")
                .strip()
                .lower()
            )

            # Convert "a)" → "a"

            if sub_question.endswith(")"):

                sub_question = (
                    sub_question[:-1]
                )

            # ------------------------------------------
            # Empty question text
            # ------------------------------------------

            if (
                not isinstance(text, str)
                or not text.strip()
            ):

                errors.append(
                    f"Q{question_number}"
                    f"{'-' + sub_question if sub_question else ''} "
                    f"has empty question text."
                )

            # ------------------------------------------
            # Identity for duplicate detection
            # ------------------------------------------

            identity = (
                question_number,
                sub_question,
            )

            identities.append(
                identity
            )

        # ==================================================
        # 4. CHECK MAIN QUESTION SEQUENCE
        # ==================================================

        actual_main_questions = set(
            question_numbers
        )

        missing_main_questions = (
            expected_main_questions
            - actual_main_questions
        )

        if missing_main_questions:

            errors.append(
                "Missing main questions: "
                + ", ".join(
                    f"Q{x}"
                    for x in sorted(
                        missing_main_questions
                    )
                )
            )

        unexpected_main_questions = (
            actual_main_questions
            - expected_main_questions
        )

        if unexpected_main_questions:

            errors.append(
                "Unexpected main questions: "
                + ", ".join(
                    f"Q{x}"
                    for x in sorted(
                        unexpected_main_questions
                    )
                )
            )

        # ==================================================
        # 5. CHECK Q1 SUBPARTS
        # ==================================================

        q1_parts = set()

        for question in questions:

            if not isinstance(question, dict):
                continue

            try:

                number = int(
                    question.get(
                        "question_number",
                        -1,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if number != 1:
                continue

            part = (
                str(
                    question.get(
                        "part",
                        "",
                    )
                    or ""
                )
                .strip()
                .lower()
            )

            if part.endswith(")"):

                part = part[:-1]

            if part:

                q1_parts.add(part)

        # ------------------------------------------
        # Missing Q1 parts
        # ------------------------------------------

        missing_q1_parts = (
            required_q1_parts
            - q1_parts
        )

        if missing_q1_parts:

            errors.append(
                "Q1 missing subparts: "
                + ", ".join(
                    sorted(
                        missing_q1_parts
                    )
                )
            )

        # ==================================================
        # 6. CHECK DUPLICATES
        # ==================================================

        counts = Counter(
            identities
        )

        duplicates = [
            identity
            for identity, count
            in counts.items()
            if count > 1
        ]

        if duplicates:

            formatted = []

            for number, part in duplicates:

                if part:

                    formatted.append(
                        f"Q{number}-{part}"
                    )

                else:

                    formatted.append(
                        f"Q{number}"
                    )

            errors.append(
                "Duplicate questions: "
                + ", ".join(
                    formatted
                )
            )

        # ==================================================
        # 7. FINAL RESULT
        # ==================================================

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }