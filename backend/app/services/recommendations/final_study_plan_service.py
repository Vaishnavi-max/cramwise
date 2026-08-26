from app.schemas.final_study_plan import (
    FinalStudyPlan,
    StudySession,
)


class M6FinalStudyPlanService:
    """
    M6.4 — Final Study Plan Service.

    Responsibilities:

        1. Validate M6.3 recommendation.
        2. Validate topic IDs.
        3. Remove completed topics.
        4. Validate prerequisites.
        5. Correct study ordering.
        6. Ensure time does not exceed availability.
        7. Build final frontend-ready study plan.

    IMPORTANT:

    M6.4 does NOT call the LLM.

    M6.3 already performs personalization.

    M6.4 is the deterministic safety layer.
    """

    def __init__(
        self,
        priority_topics: list[dict],
    ):
        """
        priority_topics:
            M5.6 priority analytics records.
        """

        self.topic_map = {
            topic["topic_id"]: topic
            for topic in priority_topics
        }

    # ======================================================
    # MAIN METHOD
    # ======================================================

    def create_plan(
        self,
        recommendation,
        subject: str,
        course_code: str,
        available_minutes: int,
        completed_topics: list[str] | None = None,
    ) -> FinalStudyPlan:
        """
        Convert M6.3 recommendation into a final
        validated study plan.
        """

        if available_minutes <= 0:

            raise ValueError(
                "available_minutes must be greater than 0."
            )

        completed = set(
            completed_topics or []
        )

        # --------------------------------------------------
        # STEP 1 — VALIDATE M6.3 STRUCTURE
        # --------------------------------------------------

        if not hasattr(
            recommendation,
            "recommendations",
        ):

            raise ValueError(
                "Invalid M6.3 recommendation object."
            )

        # --------------------------------------------------
        # STEP 2 — VALIDATE + FILTER
        # --------------------------------------------------

        valid_items = []

        seen_ids = set()

        for item in recommendation.recommendations:

            topic_id = item.topic_id

            # ----------------------------------------------
            # TOPIC MUST EXIST IN M5
            # ----------------------------------------------

            if topic_id not in self.topic_map:

                raise ValueError(
                    "M6.3 returned an unknown topic_id: "
                    f"{topic_id}"
                )

            # ----------------------------------------------
            # COMPLETED TOPIC
            # ----------------------------------------------

            if topic_id in completed:

                continue

            # ----------------------------------------------
            # DUPLICATE
            # ----------------------------------------------

            if topic_id in seen_ids:

                raise ValueError(
                    "Duplicate topic in M6.3 recommendation: "
                    f"{topic_id}"
                )

            seen_ids.add(
                topic_id
            )

            valid_items.append(
                item
            )

        # --------------------------------------------------
        # STEP 3 — DEPENDENCY VALIDATION
        # --------------------------------------------------

        self._validate_dependencies(
            items=valid_items,
            completed=completed,
        )

        # --------------------------------------------------
        # STEP 4 — ORDER TOPICS
        # --------------------------------------------------

        ordered_items = (
            self._order_topics(
                valid_items
            )
        )

        # --------------------------------------------------
        # STEP 5 — ALLOCATE TIME
        # --------------------------------------------------

        sessions = (
            self._build_sessions(
                items=ordered_items,
                available_minutes=available_minutes,
            )
        )

        # --------------------------------------------------
        # STEP 6 — TOTAL TIME
        # --------------------------------------------------

        total_minutes = sum(
            session.recommended_minutes
            for session in sessions
        )

        # --------------------------------------------------
        # STEP 7 — FINAL PLAN
        # --------------------------------------------------

        return FinalStudyPlan(
            subject=subject,
            course_code=course_code,
            available_minutes=available_minutes,
            total_planned_minutes=total_minutes,
            sessions=sessions,
            validation_status="VALID",
        )

    # ======================================================
    # DEPENDENCY VALIDATION
    # ======================================================

    def _validate_dependencies(
        self,
        items: list,
        completed: set[str],
    ) -> None:
        """
        Ensure every prerequisite is either:

            - already completed
            OR
            - included in the recommendation
            AND
            - placed before the dependent topic.
        """

        order_map = {
            item.topic_id: item.study_order
            for item in items
        }

        for item in items:

            topic = self.topic_map[
                item.topic_id
            ]

            prerequisites = topic.get(
                "prerequisites",
                []
            )

            for prerequisite_id in prerequisites:

                # ------------------------------------------
                # Already completed
                # ------------------------------------------

                if prerequisite_id in completed:
                    continue

                # ------------------------------------------
                # Prerequisite not recommended
                # ------------------------------------------

                if prerequisite_id not in order_map:

                    raise ValueError(
                        "Missing prerequisite: "
                        f"{item.topic_id} requires "
                        f"{prerequisite_id}."
                    )

                # ------------------------------------------
                # Incorrect ordering
                # ------------------------------------------

                if (
                    order_map[prerequisite_id]
                    >= item.study_order
                ):

                    raise ValueError(
                        "Invalid prerequisite order: "
                        f"{prerequisite_id} must be studied "
                        f"before {item.topic_id}."
                    )

    # ======================================================
    # ORDER TOPICS
    # ======================================================

    def _order_topics(
        self,
        items: list,
    ) -> list:
        """
        Create deterministic final study order.

        Priority:

            1. dependency depth
            2. M5 study order
            3. importance score
        """

        return sorted(
            items,
            key=lambda item: (
                self.topic_map[
                    item.topic_id
                ].get(
                    "dependency_depth",
                    0,
                ),

                self.topic_map[
                    item.topic_id
                ].get(
                    "study_order",
                    999999,
                ),

                -float(
                    self.topic_map[
                        item.topic_id
                    ].get(
                        "importance_score",
                        0,
                    )
                ),
            ),
        )

    # ======================================================
    # BUILD FINAL SESSIONS
    # ======================================================

    def _build_sessions(
        self,
        items: list,
        available_minutes: int,
    ) -> list[StudySession]:
        """
        Convert validated recommendation items into
        frontend-ready study sessions.

        The LLM's recommended minutes are respected as long
        as the final total fits within available time.
        """

        sessions = []

        remaining_minutes = (
            available_minutes
        )

        for order, item in enumerate(
            items,
            start=1,
        ):

            if remaining_minutes <= 0:
                break

            topic = self.topic_map[
                item.topic_id
            ]

            requested_minutes = (
                int(
                    item.recommended_minutes
                )
            )

            # Never exceed remaining time.

            final_minutes = min(
                requested_minutes,
                remaining_minutes,
            )

            if final_minutes <= 0:
                break

            session = StudySession(
                study_order=order,

                topic_id=item.topic_id,

                topic=topic.get(
                    "topic",
                    "",
                ),

                subtopic=topic.get(
                    "subtopic",
                ),

                unit=int(
                    topic.get(
                        "unit",
                        1,
                    )
                ),

                recommended_minutes=final_minutes,

                importance_score=float(
                    topic.get(
                        "importance_score",
                        0,
                    )
                ),

                priority=topic.get(
                    "final_priority",
                    topic.get(
                        "priority",
                        "UNKNOWN",
                    ),
                ),

                prerequisites=list(
                    topic.get(
                        "prerequisites",
                        [],
                    )
                ),

                reason=item.reason,
            )

            sessions.append(
                session
            )

            remaining_minutes -= (
                final_minutes
            )

        return sessions