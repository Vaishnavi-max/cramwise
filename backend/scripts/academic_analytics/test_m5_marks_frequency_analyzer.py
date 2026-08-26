import json
from pathlib import Path

from app.services.academic_analytics.m5_marks_frequency_analyzer import (
    M5MarksFrequencyAnalyzer
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


# ==========================================================
# M5.2 INPUT
# ==========================================================

TOPIC_ANALYTICS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "topic_analytics.json"
)


# ==========================================================
# M5.3 OUTPUT
# ==========================================================

MARKS_ANALYTICS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "marks_frequency_analytics.json"
)


# ==========================================================
# LOAD M5.2 OUTPUT
# ==========================================================

def load_topic_analytics(
    path: Path,
) -> list[dict]:
    """
    Load the persisted M5.2 topic analytics.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"M5.2 output not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


# ==========================================================
# SAVE M5.3 OUTPUT
# ==========================================================

def save_marks_analytics(
    data: list[dict],
    path: Path,
) -> None:
    """
    Persist M5.3 results so that later M5 milestones
    can directly consume them.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
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
        "M5.3 — MARKS & FREQUENCY ANALYZER TEST"
    )

    print(
        "=" * 65
    )

    # ------------------------------------------------------
    # STEP 1 — LOAD M5.2 OUTPUT
    # ------------------------------------------------------

    topics = load_topic_analytics(
        TOPIC_ANALYTICS_PATH
    )

    print(
        f"\nM5.2 topics loaded: "
        f"{len(topics)}"
    )

    assert len(topics) > 0

    # ------------------------------------------------------
    # STEP 2 — CREATE ANALYZER
    # ------------------------------------------------------

    analyzer = M5MarksFrequencyAnalyzer(
        topics
    )

    # ------------------------------------------------------
    # STEP 3 — ANALYZE
    # ------------------------------------------------------

    analyzed_topics = (
        analyzer.analyze()
    )

    print(
        f"M5.3 topics analyzed: "
        f"{len(analyzed_topics)}"
    )

    assert (
        len(analyzed_topics)
        == len(topics)
    )

    # ------------------------------------------------------
    # STEP 4 — DISPLAY SUMMARY
    # ------------------------------------------------------

    print(
        "\n--- MARKS & FREQUENCY SUMMARY ---"
    )

    for topic in analyzed_topics:

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
            f"  Max marks: "
            f"{topic['max_marks']}"
        )

        print(
            f"  Marks distribution: "
            f"{topic['marks_distribution']}"
        )

        print(
            f"  10-mark questions: "
            f"{topic['ten_mark_questions']}"
        )

        print(
            f"  5-mark questions: "
            f"{topic['five_mark_questions']}"
        )

        print(
            f"  Short questions: "
            f"{topic['short_questions']}"
        )

    # ------------------------------------------------------
    # STEP 5 — TEST HYBRID ROUTING
    # ------------------------------------------------------

    hybrid_topics = [
        topic
        for topic in analyzed_topics
        if (
            topic["subtopic"]
            and
            "hybrid routing"
            in topic["subtopic"].lower()
        )
    ]

    assert len(
        hybrid_topics
    ) > 0

    hybrid = hybrid_topics[0]

    print(
        "\n--- HYBRID ROUTING CHECK ---"
    )

    print(
        f"Question count: "
        f"{hybrid['question_count']}"
    )

    print(
        f"Total marks: "
        f"{hybrid['total_marks']}"
    )

    print(
        f"Marks distribution: "
        f"{hybrid['marks_distribution']}"
    )

    print(
        f"10-mark questions: "
        f"{hybrid['ten_mark_questions']}"
    )

    # Hybrid routing has one 10-mark question
    # in the current dataset.

    assert (
        hybrid["question_count"]
        == 1
    )

    assert (
        hybrid["total_marks"]
        == 10.0
    )

    assert (
        hybrid["ten_mark_questions"]
        == 1
    )

    # ------------------------------------------------------
    # STEP 6 — VALIDATE MARKS DISTRIBUTION
    # ------------------------------------------------------

    for topic in analyzed_topics:

        distribution_total = sum(
            topic["marks_distribution"].values()
        )

        assert (
            distribution_total
            == topic["question_count"]
        )

    print(
        "\nMarks distribution validation passed."
    )

    # ------------------------------------------------------
    # STEP 7 — VALIDATE ACTUAL QUESTIONS
    # ------------------------------------------------------

    for topic in analyzed_topics:

        for question in topic["questions"]:

            assert (
                "question_id"
                in question
            )

            assert (
                "text"
                in question
            )

    print(
        "Question preservation validation passed."
    )

    # ------------------------------------------------------
    # STEP 8 — SAVE M5.3 OUTPUT
    # ------------------------------------------------------

    save_marks_analytics(
        data=analyzed_topics,
        path=MARKS_ANALYTICS_PATH,
    )

    print(
        "\nM5.3 output saved successfully."
    )

    print(
        f"Output file:"
    )

    print(
        MARKS_ANALYTICS_PATH
    )

    # ------------------------------------------------------
    # STEP 9 — VERIFY FILE
    # ------------------------------------------------------

    assert (
        MARKS_ANALYTICS_PATH.exists()
    )

    # ------------------------------------------------------
    # STEP 10 — READ BACK JSON
    # ------------------------------------------------------

    with open(
        MARKS_ANALYTICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        saved_data = json.load(
            file
        )

    assert (
        len(saved_data)
        == len(analyzed_topics)
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
        "M5.3 Marks & Frequency Analyzer "
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