import json
from pathlib import Path


class InputService:
    """
    Handles loading and basic validation of the existing
    JSON data required by the LLM analysis layer.

    IMPORTANT:
    This service does NOT perform any LLM analysis.

    Its only job is:

        JSON file
            ↓
        Python data
            ↓
        Basic validation
            ↓
        Clean input for next layer
    """

    # ==========================================================
    # GENERIC JSON LOADER
    # ==========================================================

    def load_json(
        self,
        path: str | Path
    ):
        """
        Load any JSON file and return its Python representation.

        Parameters
        ----------
        path:
            Path of the JSON file.

        Returns
        -------
        Python object:
            Usually a list or dictionary depending on the JSON.

        Raises
        ------
        FileNotFoundError:
            If the file doesn't exist.

        json.JSONDecodeError:
            If the file is not valid JSON.
        """

        # Convert the given path into a Path object.
        path = Path(path)

        # Make sure the file actually exists before trying
        # to open it.
        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        # Open using UTF-8 because our academic data may contain
        # special characters.
        with path.open(
            "r",
            encoding="utf-8"
        ) as f:

            # Convert JSON → Python object.
            return json.load(f)

    # ==========================================================
    # LOAD ENRICHED QUESTIONS
    # ==========================================================

    def load_questions(
        self,
        path: str | Path
    ) -> list[dict]:
        """
        Load an enriched PYQ JSON file.

        Expected structure:

        [
            {
                "paper_id": "...",
                "subject": "...",
                "subject_code": "...",
                "unit": 1,
                "text": "...",
                ...
            }
        ]

        The LLM analysis layer will later use these
        questions as its input.
        """

        data = self.load_json(path)

        # We expect the question file to contain a list
        # of question objects.
        if not isinstance(data, list):
            raise ValueError(
                "Questions JSON must contain a list."
            )

        return data

    # ==========================================================
    # LOAD SYLLABUS INDEX
    # ==========================================================

    def load_syllabus_index(
        self,
        path: str | Path
    ) -> list[dict]:
        """
        Load the structured syllabus index.

        Expected structure:

        [
            {
                "index_id": "...",
                "course_code": "...",
                "unit_number": 1,
                "topic": "...",
                "subtopic": "...",
                ...
            }
        ]

        These records will later be used to give the LLM
        the available syllabus topics.
        """

        data = self.load_json(path)

        # The syllabus index should also be a list of
        # structured syllabus records.
        if not isinstance(data, list):
            raise ValueError(
                "Syllabus index JSON must contain a list."
            )

        return data

    # ==========================================================
    # VALIDATE QUESTIONS
    # ==========================================================

    def validate_questions(
        self,
        questions: list[dict]
    ) -> None:
        """
        Perform basic structural validation on questions.

        We are NOT checking whether the question is
        academically correct here.

        We only make sure that the fields required by
        the next LLM-analysis stages are present.

        Required fields:

            paper_id
            subject_code
            unit
            text
        """

        required_fields = {
            "paper_id",
            "subject_code",
            "unit",
            "text",
        }

        for i, question in enumerate(questions):

            # Make sure every item is actually a dictionary.
            if not isinstance(question, dict):
                raise ValueError(
                    f"Question {i} must be a dictionary."
                )

            # Find which required fields are missing.
            missing = (
                required_fields
                - question.keys()
            )

            if missing:
                raise ValueError(
                    f"Question {i} is missing fields: "
                    f"{sorted(missing)}"
                )

            # Make sure the actual question text isn't empty.
            if not isinstance(question["text"], str):
                raise ValueError(
                    f"Question {i} has invalid 'text'. "
                    "Expected a string."
                )

            if not question["text"].strip():
                raise ValueError(
                    f"Question {i} has empty question text."
                )

    # ==========================================================
    # VALIDATE SYLLABUS INDEX
    # ==========================================================

    def validate_syllabus_index(
        self,
        syllabus: list[dict]
    ) -> None:
        """
        Perform basic structural validation on the syllabus index.

        Required fields:

            index_id
            course_code
            unit_number
            topic
            subtopic

        These fields are important because the later LLM layer
        will use them to identify the correct syllabus topic.
        """

        required_fields = {
            "index_id",
            "course_code",
            "unit_number",
            "topic",
            "subtopic",
        }

        # Keep track of IDs so we can detect duplicate
        # syllabus records.
        seen_ids = set()

        for i, record in enumerate(syllabus):

            # Every syllabus record should be a dictionary.
            if not isinstance(record, dict):
                raise ValueError(
                    f"Syllabus record {i} must be a dictionary."
                )

            # Find missing required fields.
            missing = (
                required_fields
                - record.keys()
            )

            if missing:
                raise ValueError(
                    f"Syllabus record {i} is missing fields: "
                    f"{sorted(missing)}"
                )

            # --------------------------------------------------
            # Validate index_id
            # --------------------------------------------------

            index_id = record["index_id"]

            if not isinstance(index_id, str):
                raise ValueError(
                    f"Syllabus record {i} has invalid "
                    "'index_id'. Expected a string."
                )

            if not index_id.strip():
                raise ValueError(
                    f"Syllabus record {i} has empty "
                    "'index_id'."
                )

            # Duplicate IDs would cause problems later when
            # the LLM selects a topic by ID.
            if index_id in seen_ids:
                raise ValueError(
                    f"Duplicate syllabus index_id found: "
                    f"{index_id}"
                )

            seen_ids.add(index_id)

            # --------------------------------------------------
            # Validate course code
            # --------------------------------------------------

            if not isinstance(
                record["course_code"],
                str
            ):
                raise ValueError(
                    f"Syllabus record {i} has invalid "
                    "'course_code'."
                )

            # --------------------------------------------------
            # Validate unit number
            # --------------------------------------------------

            if not isinstance(
                record["unit_number"],
                int
            ):
                raise ValueError(
                    f"Syllabus record {i} has invalid "
                    "'unit_number'. Expected an integer."
                )

            # --------------------------------------------------
            # Validate topic
            # --------------------------------------------------

            if not isinstance(
                record["topic"],
                str
            ):
                raise ValueError(
                    f"Syllabus record {i} has invalid "
                    "'topic'."
                )

            if not record["topic"].strip():
                raise ValueError(
                    f"Syllabus record {i} has empty "
                    "'topic'."
                )