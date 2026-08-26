from pathlib import Path

from app.clients.groq_client import GroqClient

from app.schemas.recommendation import (
    RecommendationRequest
)

from app.services.llm_analysis.input_service import (
    InputService
)

from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService
)

from app.services.recommendations.topic_selector import (
    M6TopicSelector
)

from app.services.recommendations.personalized_recommendation_service import (
    M6PersonalizedRecommendationService
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
# SYLLABUS
# ==========================================================

SYLLABUS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "syllabus"
    / "syllabus_index.json"
)


# ==========================================================
# M5 PRIORITY ANALYTICS
# ==========================================================

PRIORITY_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "priority_analytics.json"
)


# ==========================================================
# TEST
# ==========================================================

def main():

    print(
        "=" * 65
    )

    print(
        "M6.3 — PERSONALIZED RECOMMENDATION TEST"
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
    # STEP 2 — CREATE M6.2
    # ======================================================

    selector = M6TopicSelector(
        catalog=catalog,
        priority_path=PRIORITY_PATH,
    )

    print(
        "M6.2 Topic Selector created."
    )

    # ======================================================
    # STEP 3 — CREATE GROQ
    # ======================================================

    print(
        "\n--- STEP 3: CREATE GROQ CLIENT ---"
    )

    groq_client = GroqClient()

    print(
        "Groq client created successfully."
    )

    # ======================================================
    # STEP 4 — CREATE M6.3
    # ======================================================

    service = (
        M6PersonalizedRecommendationService(
            topic_selector=selector,
            groq_client=groq_client,
        )
    )

    print(
        "M6.3 Personalized Recommendation "
        "Service created."
    )

    # ======================================================
    # TEST 1 — BASIC REQUEST
    # ======================================================

    print(
        "\n--- TEST 1: COMPILER DESIGN / 4 HOURS ---"
    )

    request = RecommendationRequest(
        subject="Compiler Design",
        available_hours=4,
    )

    print(
        f"Subject: {request.subject}"
    )

    print(
        f"Available hours: "
        f"{request.available_hours}"
    )

    print(
        "\nSending recommendation request to Groq..."
    )

    result = service.recommend(
        request
    )

    print(
        "\n========== M6.3 RESULT =========="
    )

    print(
        f"Total minutes: "
        f"{result.total_minutes}"
    )

    for item in result.recommendations:

        print(
            f"\n{item.study_order}. "
            f"{item.topic_id}"
        )

        print(
            f"   Minutes: "
            f"{item.recommended_minutes}"
        )

        print(
            f"   Reason: "
            f"{item.reason}"
        )

    # ------------------------------------------------------
    # BASIC ASSERTIONS
    # ------------------------------------------------------

    assert isinstance(
        result.recommendations,
        list,
    )

    assert (
        result.total_minutes
        <= 4 * 60
    )

    print(
        "\nBasic recommendation validation passed."
    )

    # ======================================================
    # TEST 2 — TOPIC ID VALIDATION
    # ======================================================

    print(
        "\n--- TEST 2: TOPIC ID VALIDATION ---"
    )

    selection = selector.select(
        request
    )

    valid_ids = {
        topic["topic_id"]
        for topic in selection[
            "candidate_topics"
        ]
    }

    for item in result.recommendations:

        assert (
            item.topic_id
            in valid_ids
        )

    print(
        "All recommended topic IDs are valid."
    )

    # ======================================================
    # TEST 3 — DUPLICATE CHECK
    # ======================================================

    print(
        "\n--- TEST 3: DUPLICATE CHECK ---"
    )

    ids = [
        item.topic_id
        for item in result.recommendations
    ]

    assert (
        len(ids)
        == len(set(ids))
    )

    print(
        "No duplicate topics found."
    )

    # ======================================================
    # TEST 4 — TIME VALIDATION
    # ======================================================

    print(
        "\n--- TEST 4: TIME VALIDATION ---"
    )

    calculated_minutes = sum(
        item.recommended_minutes
        for item in result.recommendations
    )

    assert (
        calculated_minutes
        == result.total_minutes
    )

    assert (
        calculated_minutes
        <= 240
    )

    print(
        "Study time validation passed."
    )

    # ======================================================
    # TEST 5 — COMPLETED TOPIC
    # ======================================================

    print(
        "\n--- TEST 5: COMPLETED TOPIC ---"
    )

    candidate_topics = (
        selection["candidate_topics"]
    )

    assert len(
        candidate_topics
    ) > 0

    completed_topic_id = (
        candidate_topics[0]["topic_id"]
    )

    request_with_completed = (
        RecommendationRequest(
            subject="Compiler Design",
            available_hours=4,
            completed_topics=[
                completed_topic_id
            ],
        )
    )

    result_with_completed = (
        service.recommend(
            request_with_completed
        )
    )

    returned_ids = {
        item.topic_id
        for item in (
            result_with_completed
            .recommendations
        )
    }

    assert (
        completed_topic_id
        not in returned_ids
    )

    print(
        "Completed topic was not recommended."
    )

    # ======================================================
    # TEST 6 — STRUCTURED OUTPUT
    # ======================================================

    print(
        "\n--- TEST 6: STRUCTURED OUTPUT ---"
    )

    assert isinstance(
        result.total_minutes,
        int,
    )

    for item in result.recommendations:

        assert isinstance(
            item.topic_id,
            str,
        )

        assert isinstance(
            item.study_order,
            int,
        )

        assert isinstance(
            item.recommended_minutes,
            int,
        )

        assert isinstance(
            item.reason,
            str,
        )

    print(
        "Structured output validation passed."
    )

    # ======================================================
    # TEST 7 — LLM CANDIDATE LIMIT
    # ======================================================

    print(
        "\n--- TEST 7: LLM CANDIDATE LIMIT ---"
    )

    all_topics = (
        selection["candidate_topics"]
    )

    llm_topics = (
        service._prepare_llm_candidates(
            all_topics
        )
    )

    print(
        f"All M6.2 candidates: "
        f"{len(all_topics)}"
    )

    print(
        f"Candidates sent to Groq: "
        f"{len(llm_topics)}"
    )

    assert (
        len(llm_topics)
        <= 8
    )

    assert (
        len(llm_topics)
        > 0
    )

    print(
        "Groq candidate-size optimization passed."
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    print(
        "\n" + "=" * 65
    )

    print(
        "M6.3 Personalized Recommendation "
        "tests passed successfully."
    )

    print(
        "=" * 65
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()