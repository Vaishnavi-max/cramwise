import json
import re

from pathlib import Path


class M65PyqRetrievalService:
    """
    M6.5 PYQ retrieval layer.

    Reads already-enriched PYQ JSON files.

    It does NOT:
        - OCR PDFs
        - parse questions
        - call an LLM
        - generate answers

    Existing enriched PYQs are reused directly.
    """

    def __init__(
        self,
        enriched_base_dir: str | Path = (
            "uploads/temp/enriched"
        ),
    ):
        self.enriched_base_dir = Path(
            enriched_base_dir
        )

    # ======================================================
    # NORMALIZATION
    # ======================================================

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            str(value).lower(),
        ).strip()

    @staticmethod
    def _course_code_normalized(
        course_code: str,
    ) -> str:
        return "".join(
            str(course_code)
            .upper()
            .split()
        )

    # ======================================================
    # LOAD FILES
    # ======================================================

    def _load_json_files(self) -> list[dict]:
        """
        Load all enriched PYQ JSON records.

        Supports the current structure where the
        directory contains multiple subject JSON files.
        """

        if not self.enriched_base_dir.exists():
            raise FileNotFoundError(
                "Enriched PYQ directory not found: "
                f"{self.enriched_base_dir}"
            )

        records = []

        for path in self.enriched_base_dir.rglob(
            "*.json"
        ):

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    data = json.load(file)

            except (
                json.JSONDecodeError,
                OSError,
            ):

                continue

            if isinstance(data, list):

                for item in data:

                    if isinstance(item, dict):

                        records.append(item)

            elif isinstance(data, dict):

                records.append(data)

        return records

    # ======================================================
    # KEYWORD EXTRACTION
    # ======================================================

    def _topic_keywords(
        self,
        topic: str,
        subtopic: str | None,
    ) -> set[str]:

        text = (
            f"{topic} "
            f"{subtopic or ''}"
        )

        normalized = self._normalize(
            text
        )

        stop_words = {
            "the",
            "and",
            "of",
            "to",
            "in",
            "for",
            "a",
            "an",
            "on",
            "with",
            "using",
            "based",
            "review",
            "introduction",
            "concept",
            "study",
        }

        return {
            word
            for word in normalized.split()
            if (
                len(word) >= 3
                and word not in stop_words
            )
        }

    # ======================================================
    # RELEVANCE SCORE
    # ======================================================

    def _score_pyq(
        self,
        pyq: dict,
        keywords: set[str],
    ) -> int:

        question_text = self._normalize(
            pyq.get("text", "")
        )

        if not question_text:
            return 0

        question_words = set(
            question_text.split()
        )

        overlap = keywords.intersection(
            question_words
        )

        score = len(overlap)

        # Exact topic phrase gets a strong boost.
        return score

    # ======================================================
    # RETRIEVE
    # ======================================================

    def retrieve(
        self,
        *,
        course_code: str,
        unit: int,
        topic: str,
        subtopic: str | None = None,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Retrieve the most relevant existing PYQs.

        Filtering:
            1. course
            2. unit

        Ranking:
            keyword overlap with topic/subtopic
        """

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        normalized_course = (
            self._course_code_normalized(
                course_code
            )
        )

        keywords = self._topic_keywords(
            topic,
            subtopic,
        )

        records = self._load_json_files()

        candidates = []

        for pyq in records:

            pyq_course = (
                pyq.get("subject_code")
                or ""
            )

            normalized_pyq_course = (
                self._course_code_normalized(
                    pyq_course
                )
            )

            if (
                normalized_pyq_course
                != normalized_course
            ):
                continue

            try:
                pyq_unit = int(
                    pyq.get("unit")
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if pyq_unit != int(unit):
                continue

            score = self._score_pyq(
                pyq,
                keywords,
            )

            if score <= 0:
                continue

            enriched = dict(pyq)

            enriched["_m65_relevance_score"] = (
                score
            )

            candidates.append(
                enriched
            )

        candidates.sort(
            key=lambda item: (
                -item[
                    "_m65_relevance_score"
                ],
                -float(
                    item.get(
                        "marks",
                        0,
                    ) or 0
                ),
            )
        )

        return candidates[:top_k]