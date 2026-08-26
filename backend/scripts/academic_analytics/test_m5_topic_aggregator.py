import json
from pathlib import Path

from app.services.academic_analytics.m5_result_loader import (
    M5ResultLoader
)

from app.services.academic_analytics.m5_topic_aggregator import (
    M5TopicAggregator
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


# ==========================================================
# M4 OUTPUT
# ==========================================================

ANALYSIS_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analyzed"
    / "6thsempyqs_2025"
)


# ==========================================================
# M5 OUTPUT
# ==========================================================

# M5 will maintain its own analytics directory.
#
# M4:
#   uploads/temp/analyzed/
#
# M5:
#   uploads/temp/analytics/
#
# This keeps intermediate LLM results separate from
# the higher-level analytics generated from them.

ANALYTICS_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
)


TOPIC_ANALYTICS_PATH = (
    ANALYTICS_DIR
    / "topic_analytics.json"
)


# ==========================================================
# SAVE TOPIC ANALYTICS
# ==========================================================

def save_topic_analytics(
    topics: list[dict],
    output_path: Path,
) -> None:
    """
    Save the M5.2 topic-level analytics to JSON.

    The aggregated structure contains Python sets internally,
    but M5TopicAggregator already converts those sets into
    lists before returning the final result.

    Therefore the result can be directly serialized to JSON.
    """

    # ------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------
    # WRITE JSON
    # ------------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            topics,
            file,
            indent=4,
            ensure_ascii=False,
        )


# ==========================================================
# TEST
# ==========================================================

def main():

    print(
        "=" * 65
    )

    print(
        "M5.2 — TOPIC AGGREGATOR TEST"
    )

    print(
        "=" * 65
    )

    # ------------------------------------------------------
    # STEP 1 — LOAD M4 RESULTS
    # ------------------------------------------------------

    loader = M5ResultLoader(
        ANALYSIS_DIR
    )

    results = loader.load_all()

    print(
        f"\nM4 results loaded: "
        f"{len(results)}"
    )

    # We currently have 152 successful M4 analyses.
    assert len(results) == 152

    # ------------------------------------------------------
    # STEP 2 — CREATE AGGREGATOR
    # ------------------------------------------------------

    aggregator = M5TopicAggregator(
        results
    )

    # ------------------------------------------------------
    # STEP 3 — AGGREGATE
    # ------------------------------------------------------

    topics = aggregator.aggregate()

    print(
        f"Unique topics found: "
        f"{len(topics)}"
    )

    assert len(topics) > 0

    # ------------------------------------------------------
    # STEP 4 — DISPLAY TOPIC SUMMARY
    # ------------------------------------------------------

    print(
        "\n--- TOPIC SUMMARY ---"
    )

    for topic in topics:

        print(
            f"\n{topic['topic_id']}"
        )

        print(
            f"  Topic: "
            f"{topic['topic']}"
        )

        print(
            f"  Subtopic: "
            f"{topic['subtopic']}"
        )

        print(
            f"  Unit: "
            f"{topic['unit']}"
        )

        print(
            f"  Questions: "
            f"{topic['question_count']}"
        )

        print(
            f"  Papers: "
            f"{topic['paper_count']}"
        )

        print(
            f"  Total marks: "
            f"{topic['total_marks']}"
        )

        print(
            f"  Average marks: "
            f"{topic['average_marks']:.2f}"
        )

        print(
            f"  Independent: "
            f"{topic['independent_count']}"
        )

        print(
            f"  Dependent: "
            f"{topic['dependent_count']}"
        )

        print(
            f"  Prerequisites: "
            f"{topic['prerequisites']}"
        )

    # ------------------------------------------------------
    # STEP 5 — FIND HYBRID ROUTING
    # ------------------------------------------------------

    hybrid_topics = [
        topic
        for topic in topics
        if (
            topic["subtopic"]
            and
            "hybrid routing"
            in topic["subtopic"].lower()
        )
    ]

    assert len(hybrid_topics) > 0

    hybrid = hybrid_topics[0]

    print(
        "\n--- HYBRID ROUTING CHECK ---"
    )

    print(
        hybrid
    )

    # ------------------------------------------------------
    # STEP 6 — VALIDATE QUESTION COUNT
    # ------------------------------------------------------

    # Every successful M4 result must appear exactly once
    # in the aggregated topic groups.

    total_aggregated_questions = sum(
        topic["question_count"]
        for topic in topics
    )

    assert (
        total_aggregated_questions
        == len(results)
    )

    print(
        "\nEvery M4 result was aggregated exactly once."
    )

    # ------------------------------------------------------
    # STEP 7 — VALIDATE QUESTION DATA
    # ------------------------------------------------------

    # We explicitly check that the actual PYQ text is
    # preserved inside the topic aggregation.
    #
    # This is important because later the frontend should
    # be able to say:
    #
    #   Hybrid Routing → 7 PYQs
    #
    # and then show those actual questions.

    for topic in topics:

        for question in topic["questions"]:

            assert (
                "question_id"
                in question
            )

            assert (
                "text"
                in question
            )

            assert (
                question["text"]
                is not None
            )

            assert (
                "marks"
                in question
            )

    print(
        "Question-level data validation passed."
    )

    # ------------------------------------------------------
    # STEP 8 — SAVE M5.2 OUTPUT
    # ------------------------------------------------------

    save_topic_analytics(
        topics=topics,
        output_path=TOPIC_ANALYTICS_PATH,
    )

    print(
        "\nM5.2 output saved successfully."
    )

    print(
        f"Output file:"
    )

    print(
        TOPIC_ANALYTICS_PATH
    )

    # ------------------------------------------------------
    # STEP 9 — VERIFY FILE EXISTS
    # ------------------------------------------------------

    assert (
        TOPIC_ANALYTICS_PATH.exists()
    )

    # ------------------------------------------------------
    # STEP 10 — VERIFY JSON CAN BE READ
    # ------------------------------------------------------

    with open(
        TOPIC_ANALYTICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        saved_topics = json.load(
            file
        )

    # Number of topics before and after saving
    # must be identical.

    assert (
        len(saved_topics)
        == len(topics)
    )

    # ------------------------------------------------------
    # VERIFY QUESTIONS WERE ACTUALLY SAVED
    # ------------------------------------------------------

    saved_question_count = sum(
        topic["question_count"]
        for topic in saved_topics
    )

    assert (
        saved_question_count
        == len(results)
    )

    print(
        "Saved JSON validation passed."
    )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print(
        "\n" + "=" * 65
    )

    print(
        "M5.2 Topic Aggregator tests "
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