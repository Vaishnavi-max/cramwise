from app.clients.groq_client import GroqClient

from app.schemas.recommendation import (
    RecommendationRequest,
    PersonalizedRecommendation,
)

from app.services.recommendations.topic_selector import (
    M6TopicSelector,
)


# ==========================================================
# SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are the personalized study recommendation engine
for CramWise.

Your task is to select the best syllabus topics for a
student using ONLY the supplied academic data.

IMPORTANT RULES:

1. Use ONLY the supplied topic IDs.
2. Never invent a topic_id.
3. Do not recommend completed topics.
4. Respect all prerequisite relationships.
5. A prerequisite must be studied before its dependent topic.
6. Prefer higher-importance topics.
7. Stay within the student's available study time.
8. Assign realistic study durations.
9. Give a short factual reason for each recommendation.
10. Do not provide chain-of-thought reasoning.
11. Return ONLY the requested structured JSON.

The Python application will perform additional validation
after your response.
"""


class M6PersonalizedRecommendationService:
    """
    M6.3 — Personalized Study Recommendation Service.

    Pipeline:

        M6.2 candidate topics
                ↓
        M5 importance + dependencies
                ↓
        Compact candidate set
                ↓
        Student constraints
                ↓
              Groq
                ↓
        Structured JSON
                ↓
        Pydantic validation
                ↓
        Dependency + time validation
                ↓
        Final recommendation

    Groq is used for personalization.

    Python remains responsible for:
        - valid topic IDs
        - completed-topic protection
        - prerequisite correctness
        - time limits
        - duplicate detection
        - fallback behaviour
    """

    def __init__(
        self,
        topic_selector: M6TopicSelector,
        groq_client: GroqClient,
    ):
        self.topic_selector = topic_selector
        self.groq_client = groq_client

    # ======================================================
    # MAIN RECOMMENDATION
    # ======================================================

    def recommend(
        self,
        request: RecommendationRequest,
    ) -> PersonalizedRecommendation:
        """
        Generate a personalized study recommendation.
        """

        # --------------------------------------------------
        # STEP 1 — GET M6.2 CANDIDATES
        # --------------------------------------------------

        selection = (
            self.topic_selector.select(
                request
            )
        )

        candidate_topics = (
            selection["candidate_topics"]
        )

        if not candidate_topics:

            return PersonalizedRecommendation(
                recommendations=[],
                total_minutes=0,
            )

        # --------------------------------------------------
        # STEP 2 — REDUCE CANDIDATES
        # --------------------------------------------------

        # M5 has already calculated importance and
        # dependency information.
        #
        # There is no reason to send all 19+ topics
        # to Groq.
        #
        # This keeps the request below Groq's TPM limit.

        llm_candidate_topics = (
            self._prepare_llm_candidates(
                candidate_topics
            )
        )

        # Create a separate selection object for the
        # compact LLM prompt.

        llm_selection = {
            "subject": selection["subject"],
            "course_code": selection["course_code"],
            "candidate_topics": llm_candidate_topics,
        }

        # --------------------------------------------------
        # STEP 3 — BUILD COMPACT PROMPT
        # --------------------------------------------------

        user_prompt = (
            self._build_user_prompt(
                request=request,
                selection=llm_selection,
            )
        )

        # --------------------------------------------------
        # STEP 4 — GET JSON SCHEMA
        # --------------------------------------------------

        json_schema = (
            PersonalizedRecommendation
            .model_json_schema()
        )

        # --------------------------------------------------
        # STEP 5 — CALL GROQ
        # --------------------------------------------------

        try:

            raw_result = (
                self.groq_client.generate_json(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    json_schema=json_schema,
                    schema_name="personalized_recommendation",
                )
            )

            # --------------------------------------------------
            # STEP 6 — PYDANTIC VALIDATION
            # --------------------------------------------------

            recommendation = (
                PersonalizedRecommendation
                .model_validate(
                    raw_result
                )
            )

            # --------------------------------------------------
            # STEP 7 — APPLICATION VALIDATION
            # --------------------------------------------------

            self._validate_recommendation(
                recommendation=recommendation,
                request=request,
                candidate_topics=candidate_topics,
            )

            return recommendation

        except Exception as exc:

            # --------------------------------------------------
            # STEP 8 — DETERMINISTIC FALLBACK
            # --------------------------------------------------

            print(
                "\nM6.3 LLM recommendation failed."
            )

            print(
                f"Reason: {exc}"
            )

            print(
                "Using deterministic fallback."
            )

            return self._deterministic_fallback(
                request=request,
                candidate_topics=candidate_topics,
            )

    # ======================================================
    # PREPARE COMPACT LLM CANDIDATES
    # ======================================================

    def _prepare_llm_candidates(
        self,
        candidate_topics: list[dict],
        max_candidates: int = 8,
    ) -> list[dict]:
        """
        Reduce the M6.2 candidate set before sending it
        to Groq.

        Ranking:

            1. Dependency depth
            2. Importance score
            3. M5 study order

        We keep only the strongest candidates.

        This is NOT the final recommendation.

        It is only prompt-size optimization.
        """

        ranked = sorted(
            candidate_topics,
            key=lambda topic: (
                topic.get(
                    "dependency_depth",
                    0
                ),
                -float(
                    topic.get(
                        "importance_score",
                        0
                    )
                ),
                topic.get(
                    "study_order",
                    999999
                ),
            )
        )

        return ranked[:max_candidates]

    # ======================================================
    # BUILD COMPACT PROMPT
    # ======================================================

    def _build_user_prompt(
        self,
        request: RecommendationRequest,
        selection: dict,
    ) -> str:
        """
        Build a compact prompt.

        We intentionally exclude:

            - full PYQ text
            - question lists
            - paper lists
            - marks distributions
            - study_reason
            - unnecessary analytics

        M5 has already processed that information.
        """

        available_minutes = int(
            request.available_hours * 60
        )

        prompt = f"""
STUDENT

Subject: {selection["subject"]}
Course Code: {selection["course_code"]}
Available Time: {available_minutes} minutes
Exam Type: {request.exam_type}

COMPLETED TOPICS:
{request.completed_topics}

CANDIDATE TOPICS:
"""

        for topic in selection["candidate_topics"]:

            prerequisites = topic.get(
                "prerequisites",
                []
            )

            prompt += (
                f"\n"
                f"ID: {topic['topic_id']}\n"
                f"Topic: {topic['topic']}\n"
                f"Subtopic: {topic.get('subtopic')}\n"
                f"Importance: "
                f"{topic.get('importance_score', 0)}\n"
                f"Priority: "
                f"{topic.get('final_priority', topic.get('priority', 'UNKNOWN'))}\n"
                f"Prerequisites: {prerequisites}\n"
            )

        prompt += """

TASK

Select the most useful topics for this student
within the available study time.

Rules:

- Use only the supplied topic IDs.
- Do not select completed topics.
- Respect prerequisites.
- A prerequisite must appear before its dependent topic.
- Prefer higher-importance topics.
- Assign realistic study minutes.
- Total time must not exceed available time.
- Give a short factual reason.

Return ONLY the requested JSON.
"""

        return prompt

    # ======================================================
    # VALIDATE LLM OUTPUT
    # ======================================================

    def _validate_recommendation(
        self,
        recommendation: PersonalizedRecommendation,
        request: RecommendationRequest,
        candidate_topics: list[dict],
    ) -> None:
        """
        Strictly validate the LLM response.
        """

        candidate_map = {
            topic["topic_id"]: topic
            for topic in candidate_topics
        }

        completed = set(
            request.completed_topics
        )

        selected_ids = set()

        total_minutes = 0

        # --------------------------------------------------
        # CHECK EACH RECOMMENDATION
        # --------------------------------------------------

        for item in recommendation.recommendations:

            topic_id = item.topic_id

            # --------------------------------------------------
            # VALID TOPIC ID
            # --------------------------------------------------

            if topic_id not in candidate_map:

                raise ValueError(
                    "LLM returned an invalid topic_id: "
                    f"{topic_id}"
                )

            # --------------------------------------------------
            # COMPLETED TOPIC
            # --------------------------------------------------

            if topic_id in completed:

                raise ValueError(
                    "LLM recommended an already completed "
                    f"topic: {topic_id}"
                )

            # --------------------------------------------------
            # DUPLICATE
            # --------------------------------------------------

            if topic_id in selected_ids:

                raise ValueError(
                    "LLM returned duplicate topic_id: "
                    f"{topic_id}"
                )

            selected_ids.add(
                topic_id
            )

            # --------------------------------------------------
            # TIME
            # --------------------------------------------------

            total_minutes += (
                item.recommended_minutes
            )

        # --------------------------------------------------
        # TOTAL TIME
        # --------------------------------------------------

        available_minutes = int(
            request.available_hours * 60
        )

        if total_minutes > available_minutes:

            raise ValueError(
                "LLM recommendation exceeds available "
                f"study time: {total_minutes} > "
                f"{available_minutes} minutes."
            )

        # --------------------------------------------------
        # STUDY ORDER
        # --------------------------------------------------

        orders = [
            item.study_order
            for item in recommendation.recommendations
        ]

        if len(orders) != len(set(orders)):

            raise ValueError(
                "Duplicate study_order values returned."
            )

        # --------------------------------------------------
        # DEPENDENCY ORDER
        # --------------------------------------------------

        order_map = {
            item.topic_id: item.study_order
            for item in recommendation.recommendations
        }

        for item in recommendation.recommendations:

            topic = candidate_map[
                item.topic_id
            ]

            prerequisites = topic.get(
                "prerequisites",
                []
            )

            for prerequisite_id in prerequisites:

                # Already completed.
                if prerequisite_id in completed:
                    continue

                # Required prerequisite was not selected.
                if (
                    prerequisite_id
                    not in order_map
                ):

                    raise ValueError(
                        "Recommended topic "
                        f"{item.topic_id} depends on "
                        f"{prerequisite_id}, but the "
                        "prerequisite was not completed "
                        "or recommended."
                    )

                # Dependent topic appears before prerequisite.
                if (
                    order_map[prerequisite_id]
                    >= item.study_order
                ):

                    raise ValueError(
                        "Prerequisite ordering violated: "
                        f"{prerequisite_id} must appear "
                        f"before {item.topic_id}."
                    )

        # --------------------------------------------------
        # TOTAL MINUTES CONSISTENCY
        # --------------------------------------------------

        if (
            recommendation.total_minutes
            != total_minutes
        ):

            raise ValueError(
                "total_minutes does not match the sum "
                "of recommended_minutes."
            )

    # ======================================================
    # DETERMINISTIC FALLBACK
    # ======================================================

    def _deterministic_fallback(
        self,
        request: RecommendationRequest,
        candidate_topics: list[dict],
    ) -> PersonalizedRecommendation:
        """
        Deterministic fallback used only if Groq fails.

        Strategy:

            1. Lower dependency depth first
            2. Higher importance first
            3. M5 study order as tie-breaker
            4. Respect prerequisites
            5. Fit within available time
        """

        available_minutes = int(
            request.available_hours * 60
        )

        completed = set(
            request.completed_topics
        )

        topics = sorted(
            candidate_topics,
            key=lambda topic: (
                topic.get(
                    "dependency_depth",
                    0
                ),
                -float(
                    topic.get(
                        "importance_score",
                        0
                    )
                ),
                topic.get(
                    "study_order",
                    999999
                ),
            )
        )

        selected = []

        remaining_time = (
            available_minutes
        )

        # --------------------------------------------------
        # SELECT TOPICS
        # --------------------------------------------------

        for topic in topics:

            if remaining_time <= 0:
                break

            topic_id = topic[
                "topic_id"
            ]

            if topic_id in completed:
                continue

            prerequisites = topic.get(
                "prerequisites",
                []
            )

            selected_ids = {
                item["topic_id"]
                for item in selected
            }

            dependency_missing = False

            for prerequisite_id in prerequisites:

                if prerequisite_id in completed:
                    continue

                if prerequisite_id not in selected_ids:

                    dependency_missing = True
                    break

            if dependency_missing:
                continue

            # --------------------------------------------------
            # TIME ALLOCATION
            # --------------------------------------------------

            importance = float(
                topic.get(
                    "importance_score",
                    0
                )
            )

            if importance >= 75:
                minutes = 50

            elif importance >= 55:
                minutes = 40

            elif importance >= 40:
                minutes = 30

            else:
                minutes = 20

            minutes = min(
                minutes,
                remaining_time
            )

            if minutes <= 0:
                break

            selected.append(
                {
                    "topic_id": topic_id,
                    "study_order": len(
                        selected
                    ) + 1,
                    "recommended_minutes": minutes,
                    "reason": (
                        "Selected using exam importance "
                        "and dependency-aware fallback "
                        "ranking."
                    ),
                }
            )

            remaining_time -= minutes

        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------

        total_minutes = sum(
            item["recommended_minutes"]
            for item in selected
        )

        return PersonalizedRecommendation(
            recommendations=selected,
            total_minutes=total_minutes,
        )