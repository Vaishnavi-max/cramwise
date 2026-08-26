from collections import defaultdict


class M5PriorityAnalyzer:
    """
    M5.6 — Final Priority / Study Order Analyzer

    M5.6 combines:

        M5.4 Importance Analytics
                    +
        M5.5 Dependency Analytics
                    ↓
        Final Study Priority + Study Order


    IMPORTANT DESIGN:

    M5.4 answers:

        "How important is this topic for the exam?"

    M5.5 answers:

        "What topics should be studied before this topic?"

    M5.6 answers:

        "What is the exam priority of this topic,
         and in what order should the student study it?"

    We deliberately keep these two concepts separate.

    ----------------------------------------------------------

    EXAM PRIORITY

    Comes directly from M5.4 importance_score.

        75+  → VERY HIGH
        55+  → HIGH
        40+  → MEDIUM
        <40  → LOW

    ----------------------------------------------------------

    STUDY ORDER

    Determined using prerequisites.

    Example:

        A = importance 90
        B = importance 60

        B → A

    Even though A is more important:

        1. B
        2. A

    because B must be studied first.

    ----------------------------------------------------------

    M5.6 DOES NOT:

        - call the LLM
        - recalculate exam importance
        - add arbitrary dependency bonuses
        - modify M5.4 scores

    It only creates a dependency-aware study sequence.
    """

    def __init__(
        self,
        importance_analytics: list[dict],
        dependency_analytics: list[dict],
    ):
        """
        Receive the outputs of M5.4 and M5.5.
        """

        self.importance_analytics = (
            importance_analytics
        )

        self.dependency_analytics = (
            dependency_analytics
        )

        # --------------------------------------------------
        # FAST LOOKUP MAPS
        #
        # topic_id -> topic record
        # --------------------------------------------------

        self.importance_map = {
            item["topic_id"]: item
            for item in importance_analytics
        }

        self.dependency_map = {
            item["topic_id"]: item
            for item in dependency_analytics
        }

        # --------------------------------------------------
        # MAKE SURE BOTH ANALYTICS FILES REFER TO THE
        # SAME TOPICS.
        # --------------------------------------------------

        self._validate_topic_alignment()

    # ======================================================
    # MAIN ANALYSIS
    # ======================================================

    def analyze(self) -> list[dict]:
        """
        Generate the final M5.6 dataset.

        For every topic we create:

            topic information
            importance score
            final priority
            prerequisites
            dependency depth
            study reason

        Then we calculate study_order separately.
        """

        results = []

        # --------------------------------------------------
        # STEP 1 — COMBINE M5.4 + M5.5
        # --------------------------------------------------

        for topic_id in self.importance_map:

            importance = (
                self.importance_map[
                    topic_id
                ]
            )

            dependency = (
                self.dependency_map[
                    topic_id
                ]
            )

            # --------------------------------------------------
            # IMPORTANCE SCORE
            # --------------------------------------------------
            #
            # IMPORTANT:
            #
            # We DO NOT modify this score.
            #
            # It is the score calculated by M5.4.
            #

            importance_score = float(
                importance[
                    "importance_score"
                ]
            )

            # --------------------------------------------------
            # FINAL PRIORITY
            # --------------------------------------------------
            #
            # Priority comes directly from the M5.4 score.
            #
            # We use our M5.6 thresholds here instead of
            # trusting a previous label, so the output is
            # always consistent with the score.

            final_priority = (
                self._get_priority_label(
                    importance_score
                )
            )

            # --------------------------------------------------
            # STUDY REASON
            # --------------------------------------------------

            study_reason = (
                self._build_study_reason(
                    importance=importance,
                    dependency=dependency,
                    priority=final_priority,
                )
            )

            # --------------------------------------------------
            # CLEAN FINAL RECORD
            # --------------------------------------------------

            result = {

                # ------------------------------------------
                # TOPIC
                # ------------------------------------------

                "topic_id": topic_id,

                "topic": importance[
                    "topic"
                ],

                "subtopic": importance[
                    "subtopic"
                ],

                "unit": importance[
                    "unit"
                ],

                # ------------------------------------------
                # EXAM IMPORTANCE
                # ------------------------------------------

                "importance_score": (
                    importance_score
                ),

                "final_priority": (
                    final_priority
                ),

                # ------------------------------------------
                # DEPENDENCIES
                # ------------------------------------------

                "prerequisites": (
                    dependency.get(
                        "prerequisites",
                        [],
                    )
                ),

                "dependency_depth": (
                    dependency.get(
                        "dependency_depth",
                        0,
                    )
                ),

                # ------------------------------------------
                # STUDY ORDER
                # ------------------------------------------
                #
                # Filled after dependency-aware sorting.

                "study_order": None,

                # ------------------------------------------
                # EXPLANATION
                # ------------------------------------------

                "study_reason": study_reason,
            }

            results.append(
                result
            )

        # --------------------------------------------------
        # STEP 2 — CREATE DEPENDENCY-AWARE STUDY ORDER
        # --------------------------------------------------

        ordered_results = (
            self._create_study_order(
                results
            )
        )

        # --------------------------------------------------
        # STEP 3 — ASSIGN STUDY ORDER NUMBERS
        # --------------------------------------------------

        for index, result in enumerate(
            ordered_results,
            start=1,
        ):

            result[
                "study_order"
            ] = index

        return ordered_results

    # ======================================================
    # PRIORITY LABEL
    # ======================================================

    def _get_priority_label(
        self,
        score: float,
    ) -> str:
        """
        Convert M5.4 importance score into final priority.

            75–100 → VERY HIGH
            55–74  → HIGH
            40–54  → MEDIUM
            <40    → LOW

        IMPORTANT:

        This function does NOT modify the score.
        It only converts the score into a label.
        """

        if score >= 75:

            return "VERY HIGH"

        if score >= 55:

            return "HIGH"

        if score >= 40:

            return "MEDIUM"

        return "LOW"

    # ======================================================
    # STUDY REASON
    # ======================================================

    def _build_study_reason(
        self,
        importance: dict,
        dependency: dict,
        priority: str,
    ) -> list[str]:
        """
        Create short deterministic explanations for
        the student's study recommendation.

        These are NOT generated by the LLM.
        """

        reasons = []

        # --------------------------------------------------
        # PRIORITY
        # --------------------------------------------------

        reasons.append(
            f"Exam priority: {priority}"
        )

        # --------------------------------------------------
        # QUESTION FREQUENCY
        # --------------------------------------------------

        question_count = int(
            importance.get(
                "question_count",
                0,
            )
        )

        if question_count > 1:

            reasons.append(
                "Asked multiple times in "
                "previous-year papers."
            )

        elif question_count == 1:

            reasons.append(
                "Appeared in previous-year papers."
            )

        # --------------------------------------------------
        # MARKS
        # --------------------------------------------------

        average_marks = float(
            importance.get(
                "average_marks",
                0,
            )
        )

        if average_marks >= 8:

            reasons.append(
                "Usually appears as a "
                "high-mark question."
            )

        # --------------------------------------------------
        # PAPER RECURRENCE
        # --------------------------------------------------

        paper_count = int(
            importance.get(
                "paper_count",
                0,
            )
        )

        if paper_count > 1:

            reasons.append(
                "Repeated across multiple papers."
            )

        # --------------------------------------------------
        # PREREQUISITE FOR OTHER TOPICS
        # --------------------------------------------------

        dependent_count = int(
            dependency.get(
                "dependent_count",
                0,
            )
        )

        if dependent_count > 0:

            reasons.append(
                "Acts as a prerequisite for "
                "other syllabus topics."
            )

        # --------------------------------------------------
        # HAS PREREQUISITES
        # --------------------------------------------------

        prerequisites = dependency.get(
            "prerequisites",
            [],
        )

        if prerequisites:

            reasons.append(
                "Should be studied after its "
                "prerequisite topics."
            )

        # --------------------------------------------------
        # UNRESOLVED PREREQUISITES
        # --------------------------------------------------

        unresolved = dependency.get(
            "unresolved_prerequisites",
            [],
        )

        if unresolved:

            reasons.append(
                "Has unresolved prerequisite "
                "references that need review."
            )

        # --------------------------------------------------
        # CIRCULAR DEPENDENCIES
        # --------------------------------------------------

        cycles = dependency.get(
            "dependency_cycles",
            [],
        )

        if cycles:

            reasons.append(
                "Contains a detected dependency "
                "cycle and should be reviewed."
            )

        return reasons

    # ======================================================
    # CREATE STUDY ORDER
    # ======================================================

    def _create_study_order(
        self,
        results: list[dict],
    ) -> list[dict]:
        """
        Create a dependency-aware study sequence.

        Algorithm:

            1. Find topics with no prerequisites.
            2. Among available topics, choose the one with
               the highest importance_score.
            3. Mark it as completed.
            4. This may unlock dependent topics.
            5. Again choose the highest-importance available
               topic.
            6. Continue until all topics are ordered.

        This is a priority-based topological sort.
        """

        # --------------------------------------------------
        # QUICK LOOKUP
        # --------------------------------------------------

        result_map = {
            item["topic_id"]: item
            for item in results
        }

        topic_ids = set(
            result_map.keys()
        )

        # --------------------------------------------------
        # BUILD REVERSE DEPENDENCY GRAPH
        #
        # prerequisite → dependent topics
        #
        # Example:
        #
        # B → A
        #
        # means:
        #
        # A depends on B
        # --------------------------------------------------

        dependents = defaultdict(list)

        # Number of prerequisites still blocking each topic.

        remaining_prerequisites = {
            topic_id: 0
            for topic_id in topic_ids
        }

        # --------------------------------------------------
        # READ ALL PREREQUISITES
        # --------------------------------------------------

        for item in results:

            topic_id = item[
                "topic_id"
            ]

            prerequisites = item[
                "prerequisites"
            ]

            for prerequisite_id in prerequisites:

                # ------------------------------------------
                # UNKNOWN PREREQUISITE
                # ------------------------------------------
                #
                # M5.5 already recorded unresolved IDs.
                #
                # We cannot use an unknown topic to block
                # study ordering because it isn't part of
                # our dataset.

                if (
                    prerequisite_id
                    not in topic_ids
                ):

                    continue

                # ------------------------------------------
                # ADD GRAPH EDGE
                # ------------------------------------------

                dependents[
                    prerequisite_id
                ].append(
                    topic_id
                )

                # ------------------------------------------
                # THIS TOPIC IS BLOCKED BY ONE MORE
                # PREREQUISITE
                # ------------------------------------------

                remaining_prerequisites[
                    topic_id
                ] += 1

        # --------------------------------------------------
        # INITIAL AVAILABLE TOPICS
        # --------------------------------------------------
        #
        # These topics have no known prerequisites.

        available = [
            topic_id
            for topic_id in topic_ids
            if (
                remaining_prerequisites[
                    topic_id
                ]
                == 0
            )
        ]

        ordered = []

        # --------------------------------------------------
        # PRIORITY-BASED TOPOLOGICAL SORT
        # --------------------------------------------------

        while available:

            # ----------------------------------------------
            # SORT AVAILABLE TOPICS
            #
            # Highest importance first.
            #
            # If equal:
            #   smaller dependency depth first.
            #
            # If still equal:
            #   topic_id gives deterministic output.
            # ----------------------------------------------

            available.sort(
                key=lambda topic_id: (
                    -result_map[
                        topic_id
                    ][
                        "importance_score"
                    ],

                    result_map[
                        topic_id
                    ][
                        "dependency_depth"
                    ],

                    topic_id,
                )
            )

            # ----------------------------------------------
            # SELECT HIGHEST-IMPORTANCE AVAILABLE TOPIC
            # ----------------------------------------------

            current = available.pop(
                0
            )

            ordered.append(
                result_map[
                    current
                ]
            )

            # ----------------------------------------------
            # UNLOCK DEPENDENT TOPICS
            # ----------------------------------------------

            for dependent_id in (
                dependents.get(
                    current,
                    [],
                )
            ):

                remaining_prerequisites[
                    dependent_id
                ] -= 1

                # ------------------------------------------
                # ALL KNOWN PREREQUISITES COMPLETED
                # ------------------------------------------

                if (
                    remaining_prerequisites[
                        dependent_id
                    ]
                    == 0
                ):

                    available.append(
                        dependent_id
                    )

        # --------------------------------------------------
        # SAFETY NET
        # --------------------------------------------------
        #
        # If topics remain, they are involved in a cycle
        # or another dependency problem.
        #
        # M5.5 has already recorded those problems.
        #
        # We do NOT crash M5.6.
        #
        # We place those topics at the end according to
        # importance_score.

        if (
            len(ordered)
            != len(results)
        ):

            ordered_ids = {
                item["topic_id"]
                for item in ordered
            }

            remaining = [
                item
                for item in results
                if (
                    item["topic_id"]
                    not in ordered_ids
                )
            ]

            remaining.sort(
                key=lambda item: (
                    -item[
                        "importance_score"
                    ],

                    item[
                        "topic_id"
                    ],
                )
            )

            ordered.extend(
                remaining
            )

        return ordered

    # ======================================================
    # DATASET VALIDATION
    # ======================================================

    def _validate_topic_alignment(
        self,
    ) -> None:
        """
        Verify that M5.4 and M5.5 contain exactly the
        same topic IDs.
        """

        importance_ids = set(
            self.importance_map.keys()
        )

        dependency_ids = set(
            self.dependency_map.keys()
        )

        # --------------------------------------------------
        # MISSING FROM DEPENDENCY ANALYTICS
        # --------------------------------------------------

        only_importance = (
            importance_ids
            - dependency_ids
        )

        if only_importance:

            raise ValueError(
                "Topics present in importance analytics "
                "but missing from dependency analytics: "
                f"{sorted(only_importance)}"
            )

        # --------------------------------------------------
        # MISSING FROM IMPORTANCE ANALYTICS
        # --------------------------------------------------

        only_dependency = (
            dependency_ids
            - importance_ids
        )

        if only_dependency:

            raise ValueError(
                "Topics present in dependency analytics "
                "but missing from importance analytics: "
                f"{sorted(only_dependency)}"
            )