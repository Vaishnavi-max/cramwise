from collections import defaultdict


class M5TopicAggregator:
    """
    M5.2 — Topic Aggregator

    Takes the clean M4 results produced by M5.1 and groups
    questions according to the syllabus topic selected by M4.

    Example:

        Q1 -> Hybrid Routing
        Q2 -> MAC Protocols
        Q3 -> Hybrid Routing
        Q4 -> Hybrid Routing

    becomes:

        Hybrid Routing
            question_count = 3
            questions = [Q1, Q3, Q4]

    IMPORTANT:

    This class does NOT calculate importance.

    It only builds the raw topic-level statistics that
    later M5 modules will use.
    """

    def __init__(
        self,
        results: list[dict],
    ):
        """
        Parameters
        ----------
        results:
            Successful M4 results returned by
            M5ResultLoader.load_all().
        """

        self.results = results

    # ======================================================
    # AGGREGATE
    # ======================================================

    def aggregate(self) -> list[dict]:
        """
        Group all M4 results by topic_id.

        Returns
        -------
        list[dict]

        One dictionary is produced for every topic that
        appeared in the analyzed PYQs.
        """

        # --------------------------------------------------
        # GROUP STORAGE
        # --------------------------------------------------

        # Dictionary structure:

        # {
        #     topic_id: {
        #         "topic_id": ...,
        #         "questions": [...]
        #     }
        # }

        grouped = {}

        # --------------------------------------------------
        # PROCESS EVERY QUESTION
        # --------------------------------------------------

        for result in self.results:

            question = result["question"]
            analysis = result["analysis"]

            topic_id = analysis["topic_id"]

            # --------------------------------------------------
            # CREATE TOPIC ENTRY IF NEEDED
            # --------------------------------------------------

            if topic_id not in grouped:

                grouped[topic_id] = {
                    "topic_id": topic_id,

                    # These are copied from M4.
                    "topic": analysis["topic"],
                    "subtopic": analysis["subtopic"],

                    # Unit comes from the original PYQ.
                    "unit": question.get("unit"),

                    # All questions mapped to this topic.
                    "questions": [],

                    # Unique papers will be calculated later.
                    "papers": set(),

                    # Total marks will be calculated here.
                    "total_marks": 0.0,

                    # Dependency information from M4.
                    "prerequisites": set(),

                    # Track whether questions are independent.
                    "independent_count": 0,
                    "dependent_count": 0,
                }

            entry = grouped[topic_id]

            # --------------------------------------------------
            # STORE QUESTION
            # --------------------------------------------------

            entry["questions"].append(
                {
                    "question_id": self._get_question_id(
                        question
                    ),

                    "paper_id": question.get(
                        "paper_id"
                    ),

                    "question_number": question.get(
                        "question_number"
                    ),

                    "sub_question": question.get(
                        "sub_question"
                    ),

                    "text": question.get(
                        "text"
                    ),

                    "marks": question.get(
                        "marks"
                    ),

                    "exam_type": question.get(
                        "exam_type"
                    ),

                    "semester": question.get(
                        "semester"
                    ),
                }
            )

            # --------------------------------------------------
            # PAPER
            # --------------------------------------------------

            paper_id = question.get(
                "paper_id"
            )

            if paper_id:
                entry["papers"].add(
                    paper_id
                )

            # --------------------------------------------------
            # MARKS
            # --------------------------------------------------

            marks = question.get(
                "marks"
            )

            if marks is not None:

                try:

                    entry["total_marks"] += float(
                        marks
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    # Ignore malformed marks rather than
                    # crashing the complete aggregation.
                    pass

            # --------------------------------------------------
            # INDEPENDENCY
            # --------------------------------------------------

            if analysis.get(
                "is_independent",
                False,
            ):

                entry[
                    "independent_count"
                ] += 1

            else:

                entry[
                    "dependent_count"
                ] += 1

            # --------------------------------------------------
            # PREREQUISITES
            # --------------------------------------------------

            prerequisites = analysis.get(
                "prerequisites",
                []
            )

            for prerequisite_id in prerequisites:

                entry[
                    "prerequisites"
                ].add(
                    prerequisite_id
                )

        # ======================================================
        # CONVERT INTERNAL SETS → JSON-FRIENDLY LISTS
        # ======================================================

        aggregated = []

        for entry in grouped.values():

            # Unique papers.
            entry["papers"] = sorted(
                entry["papers"]
            )

            # Unique prerequisite IDs.
            entry["prerequisites"] = sorted(
                entry["prerequisites"]
            )

            # Basic counts.
            entry["question_count"] = len(
                entry["questions"]
            )

            entry["paper_count"] = len(
                entry["papers"]
            )

            # --------------------------------------------------
            # AVERAGE MARKS
            # --------------------------------------------------

            if entry["question_count"] > 0:

                entry["average_marks"] = (
                    entry["total_marks"]
                    / entry["question_count"]
                )

            else:

                entry["average_marks"] = 0.0

            aggregated.append(
                entry
            )

        # ------------------------------------------------------
        # SORT
        # ------------------------------------------------------

        # At this stage we are NOT ranking by importance.
        #
        # We simply make the output deterministic by sorting
        # according to topic_id.

        aggregated.sort(
            key=lambda item: item["topic_id"]
        )

        return aggregated

    # ======================================================
    # QUESTION ID
    # ======================================================

    @staticmethod
    def _get_question_id(
        question: dict,
    ) -> str:
        """
        Generate a stable question identifier.

        Examples:

            BCS_302_ENDTERM_Q5

            BCS_302_ENDTERM_Q1_a
        """

        paper_id = question.get(
            "paper_id",
            "UNKNOWN",
        )

        question_number = question.get(
            "question_number",
            "UNKNOWN",
        )

        sub_question = question.get(
            "sub_question"
        )

        if sub_question:

            return (
                f"{paper_id}"
                f"_Q{question_number}"
                f"_{sub_question}"
            )

        return (
            f"{paper_id}"
            f"_Q{question_number}"
        )