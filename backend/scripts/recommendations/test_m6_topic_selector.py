from pathlib import Path

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
# M5 PRIORITY OUTPUT
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
        "M6.2 — SUBJECT RESOLVER + TOPIC SELECTOR TEST"
    )

    print(
        "=" * 65
    )

    # ======================================================
    # STEP 1 — LOAD SYLLABUS
    # ======================================================

    print(
        "\n--- STEP 1: LOAD M2 SYLLABUS ---"
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

    print(
        f"Syllabus records loaded: "
        f"{len(syllabus)}"
    )

    # ======================================================
    # STEP 2 — CREATE M2
    # ======================================================

    catalog = (
        SyllabusCatalogService(
            syllabus
        )
    )

    print(
        "M2 Syllabus Catalog created."
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
    # TEST 1 — RESOLVE SUBJECT
    # ======================================================

    print(
        "\n--- TEST 1: SUBJECT RESOLUTION ---"
    )

    course_code = (
        selector.resolve_subject(
            "Compiler Design"
        )
    )

    print(
        f"Compiler Design → {course_code}"
    )

    assert (
        course_code.replace(" ", "").upper()
        == "BCS306"
    )

    print(
        "Subject resolution passed."
    )

    # ======================================================
    # TEST 2 — CASE INSENSITIVE RESOLUTION
    # ======================================================

    print(
        "\n--- TEST 2: CASE-INSENSITIVE RESOLUTION ---"
    )

    course_code = (
        selector.resolve_subject(
            "compiler design"
        )
    )

    print(
        f"compiler design → {course_code}"
    )

    assert (
        course_code.replace(" ", "").upper()
        == "BCS306"
    )

    print(
        "Case-insensitive resolution passed."
    )

    # ======================================================
    # TEST 3 — GET SUBJECT TOPICS
    # ======================================================

    print(
        "\n--- TEST 3: GET SUBJECT TOPICS ---"
    )

    topics = (
        selector.get_subject_topics(
            course_code
        )
    )

    print(
        f"Compiler Design topics: "
        f"{len(topics)}"
    )

    assert len(topics) > 0

    for topic in topics[:5]:

        print(
            f"  {topic['topic_id']} | "
            f"{topic['topic']} | "
            f"{topic['subtopic']}"
        )

    print(
        "Subject topic retrieval passed."
    )

    # ======================================================
    # TEST 4 — BASIC SELECTION
    # ======================================================

    print(
        "\n--- TEST 4: BASIC TOPIC SELECTION ---"
    )

    request = RecommendationRequest(
        subject="Compiler Design",
        available_hours=4,
    )

    result = selector.select(
        request
    )

    print(
        f"\nSubject: "
        f"{result['subject']}"
    )

    print(
        f"Course code: "
        f"{result['course_code']}"
    )

    print(
        f"Total topics: "
        f"{result['total_topics']}"
    )

    print(
        f"Completed topics: "
        f"{result['completed_topics']}"
    )

    print(
        f"Candidate topics: "
        f"{len(result['candidate_topics'])}"
    )

    assert (
        result["course_code"]
        .replace(" ", "")
        .upper()
        == "BCS306"
    )

    assert (
        len(result["candidate_topics"])
        > 0
    )

    print(
        "Basic topic selection passed."
    )

    # ======================================================
    # TEST 5 — COMPLETED TOPICS ARE REMOVED
    # ======================================================

    print(
        "\n--- TEST 5: REMOVE COMPLETED TOPICS ---"
    )

    first_topic_id = (
        topics[0]["topic_id"]
    )

    request = RecommendationRequest(
        subject="Compiler Design",
        available_hours=4,
        completed_topics=[
            first_topic_id
        ],
    )

    result = selector.select(
        request
    )

    candidate_ids = {
        topic["topic_id"]
        for topic in result[
            "candidate_topics"
        ]
    }

    print(
        f"Completed topic: "
        f"{first_topic_id}"
    )

    print(
        f"Remaining topics: "
        f"{len(candidate_ids)}"
    )

    assert (
        first_topic_id
        not in candidate_ids
    )

    assert (
        result["completed_topics"]
        == 1
    )

    print(
        "Completed-topic filtering passed."
    )

    # ======================================================
    # TEST 6 — UNKNOWN SUBJECT
    # ======================================================

    print(
        "\n--- TEST 6: UNKNOWN SUBJECT ---"
    )

    try:

        selector.resolve_subject(
            "This Subject Does Not Exist"
        )

        raise AssertionError(
            "Unknown subject should have failed."
        )

    except ValueError:

        print(
            "Unknown subject correctly rejected."
        )

    # ======================================================
    # TEST 7 — INVALID PRIORITY DATA
    # ======================================================

    print(
        "\n--- TEST 7: PRIORITY DATA ---"
    )

    assert (
        selector.priority_data
    )

    print(
        f"Priority records loaded: "
        f"{len(selector.priority_data)}"
    )

    print(
        "Priority analytics loading passed."
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    print(
        "\n" + "=" * 65
    )

    print(
        "M6.2 Subject Resolver + Topic "
        "Selector tests passed successfully."
    )

    print(
        "=" * 65
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()