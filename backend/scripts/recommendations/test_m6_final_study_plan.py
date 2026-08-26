import json

from pathlib import Path

from app.clients.groq_client import GroqClient

from app.schemas.recommendation import (
    RecommendationRequest,
)

from app.services.llm_analysis.input_service import (
    InputService,
)

from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService,
)

from app.services.recommendations.topic_selector import (
    M6TopicSelector,
)

from app.services.recommendations.personalized_recommendation_service import (
    M6PersonalizedRecommendationService,
)

from app.services.recommendations.final_study_plan_service import (
    M6FinalStudyPlanService,
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


# ==========================================================
# INPUT PATHS
# ==========================================================

SYLLABUS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "syllabus"
    / "syllabus_index.json"
)

PRIORITY_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "priority_analytics.json"
)


# ==========================================================
# LOAD PRIORITY DATA
# ==========================================================

def load_priority_topics() -> list[dict]:
    """
    Load M5.6 priority analytics.
    """

    with open(
        PRIORITY_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ==========================================================
# TEST
# ==========================================================

def main():

    print(
        "=" * 65
    )

    print(
        "M6.4 — FINAL STUDY PLAN TEST"
    )

    print(
        "=" * 65
    )

    # ======================================================
    # STEP 1 — LOAD M2
    # ======================================================

    print(
        "\n--- STEP 1: LOAD M2 ---"
    )

    input_service = InputService()

    syllabus = (
        input_service.load_syllabus_index(
            SYLLABUS_PATH
        )
    )

    input_service.validate_syllabus_index(
        syllabus
    )

    catalog = (
        SyllabusCatalogService(
            syllabus
        )
    )

    print(
        f"Syllabus records: "
        f"{len(syllabus)}"
    )

    # ======================================================
    # STEP 2 — LOAD M5.6
    # ======================================================

    print(
        "\n--- STEP 2: LOAD M5.6 ---"
    )

    priority_topics = (
        load_priority_topics()
    )

    print(
        f"Priority topics: "
        f"{len(priority_topics)}"
    )

    assert (
        len(priority_topics) > 0
    )

    # ======================================================
    # STEP 3 — CREATE M6.2
    # ======================================================

    selector = M6TopicSelector(
        catalog=catalog,
        priority_path=PRIORITY_PATH,
    )

    print(
        "M6.2 Topic Selector created."
    )

    # ======================================================
    # STEP 4 — CREATE M6.3
    # ======================================================

    groq_client = GroqClient()

    m63 = (
        M6PersonalizedRecommendationService(
            topic_selector=selector,
            groq_client=groq_client,
        )
    )

    print(
        "M6.3 Recommendation Service created."
    )

    # ======================================================
    # STEP 5 — GENERATE M6.3 RECOMMENDATION
    # ======================================================

    print(
        "\n--- STEP 3: GENERATE M6.3 RECOMMENDATION ---"
    )

    request = RecommendationRequest(
        subject="Compiler Design",
        available_hours=4,
        exam_type="ENDTERM",
        completed_topics=[],
    )

    recommendation = (
        m63.recommend(
            request
        )
    )

    print(
        f"M6.3 topics: "
        f"{len(recommendation.recommendations)}"
    )

    print(
        f"M6.3 minutes: "
        f"{recommendation.total_minutes}"
    )

    assert (
        recommendation.total_minutes
        <= 240
    )

    # ======================================================
    # STEP 6 — CREATE M6.4
    # ======================================================

    print(
        "\n--- STEP 4: CREATE M6.4 ---"
    )

    m64 = (
        M6FinalStudyPlanService(
            priority_topics=priority_topics,
        )
    )

    print(
        "M6.4 Final Study Plan Service created."
    )

    # ======================================================
    # STEP 7 — BUILD FINAL PLAN
    # ======================================================

    print(
        "\n--- STEP 5: BUILD FINAL PLAN ---"
    )

    final_plan = (
        m64.create_plan(
            recommendation=recommendation,
            subject=request.subject,
            course_code="BCS 306",
            available_minutes=240,
            completed_topics=request.completed_topics,
        )
    )

    print(
        "\n========== FINAL STUDY PLAN =========="
    )

    print(
        f"Subject: "
        f"{final_plan.subject}"
    )

    print(
        f"Course Code: "
        f"{final_plan.course_code}"
    )

    print(
        f"Available: "
        f"{final_plan.available_minutes} minutes"
    )

    print(
        f"Planned: "
        f"{final_plan.total_planned_minutes} minutes"
    )

    print(
        f"Status: "
        f"{final_plan.validation_status}"
    )

    for session in final_plan.sessions:

        print(
            f"\n{session.study_order}. "
            f"{session.topic_id}"
        )

        print(
            f"   Topic: "
            f"{session.topic}"
        )

        print(
            f"   Subtopic: "
            f"{session.subtopic}"
        )

        print(
            f"   Unit: "
            f"{session.unit}"
        )

        print(
            f"   Minutes: "
            f"{session.recommended_minutes}"
        )

        print(
            f"   Importance: "
            f"{session.importance_score}"
        )

        print(
            f"   Priority: "
            f"{session.priority}"
        )

        print(
            f"   Prerequisites: "
            f"{session.prerequisites}"
        )

        print(
            f"   Reason: "
            f"{session.reason}"
        )

    # ======================================================
    # TEST 1 — PLAN STATUS
    # ======================================================

    print(
        "\n--- TEST 1: PLAN STATUS ---"
    )

    assert (
        final_plan.validation_status
        == "VALID"
    )

    print(
        "Final plan status validation passed."
    )

    # ======================================================
    # TEST 2 — TIME
    # ======================================================

    print(
        "\n--- TEST 2: TIME VALIDATION ---"
    )

    assert (
        final_plan.total_planned_minutes
        <= final_plan.available_minutes
    )

    calculated_time = sum(
        session.recommended_minutes
        for session in final_plan.sessions
    )

    assert (
        calculated_time
        == final_plan.total_planned_minutes
    )

    print(
        "Final plan time validation passed."
    )

    # ======================================================
    # TEST 3 — UNIQUE TOPICS
    # ======================================================

    print(
        "\n--- TEST 3: DUPLICATE CHECK ---"
    )

    topic_ids = [
        session.topic_id
        for session in final_plan.sessions
    ]

    assert (
        len(topic_ids)
        == len(set(topic_ids))
    )

    print(
        "No duplicate topics found."
    )

    # ======================================================
    # TEST 4 — VALID TOPIC IDS
    # ======================================================

    print(
        "\n--- TEST 4: TOPIC ID VALIDATION ---"
    )

    valid_ids = {
        topic["topic_id"]
        for topic in priority_topics
    }

    for session in final_plan.sessions:

        assert (
            session.topic_id
            in valid_ids
        )

    print(
        "All final topic IDs are valid."
    )

    # ======================================================
    # TEST 5 — STUDY ORDER
    # ======================================================

    print(
        "\n--- TEST 5: STUDY ORDER ---"
    )

    orders = [
        session.study_order
        for session in final_plan.sessions
    ]

    assert (
        orders
        == list(
            range(
                1,
                len(orders) + 1,
            )
        )
    )

    print(
        "Study order validation passed."
    )

    # ======================================================
    # TEST 6 — COMPLETED TOPIC
    # ======================================================

    print(
        "\n--- TEST 6: COMPLETED TOPIC ---"
    )

    if final_plan.sessions:

        completed_id = (
            final_plan.sessions[0]
            .topic_id
        )

        completed_request = (
            RecommendationRequest(
                subject="Compiler Design",
                available_hours=4,
                exam_type="ENDTERM",
                completed_topics=[
                    completed_id
                ],
            )
        )

        completed_recommendation = (
            m63.recommend(
                completed_request
            )
        )

        completed_plan = (
            m64.create_plan(
                recommendation=(
                    completed_recommendation
                ),
                subject="Compiler Design",
                course_code="BCS 306",
                available_minutes=240,
                completed_topics=[
                    completed_id
                ],
            )
        )

        returned_ids = {
            session.topic_id
            for session in completed_plan.sessions
        }

        assert (
            completed_id
            not in returned_ids
        )

        print(
            "Completed topic was excluded."
        )

    # ======================================================
    # TEST 7 — FRONTEND STRUCTURE
    # ======================================================

    print(
        "\n--- TEST 7: FRONTEND STRUCTURE ---"
    )

    dumped = (
        final_plan.model_dump()
    )

    assert (
        "subject"
        in dumped
    )

    assert (
        "course_code"
        in dumped
    )

    assert (
        "available_minutes"
        in dumped
    )

    assert (
        "total_planned_minutes"
        in dumped
    )

    assert (
        "sessions"
        in dumped
    )

    assert isinstance(
        dumped["sessions"],
        list,
    )

    print(
        "Frontend-ready structure validation passed."
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    print(
        "\n" + "=" * 65
    )

    print(
        "M6.4 Final Study Plan tests "
        "passed successfully."
    )

    print(
        "=" * 65
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()