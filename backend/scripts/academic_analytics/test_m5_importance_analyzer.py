import json
from pathlib import Path

from app.services.academic_analytics.m5_importance_analyzer import (
    M5ImportanceAnalyzer
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


# ==========================================================
# M5.3 INPUT
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
# M5.4 OUTPUT
# ==========================================================

IMPORTANCE_ANALYTICS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "importance_analytics.json"
)


# ==========================================================
# LOAD M5.3
# ==========================================================

def load_marks_analytics(
    path: Path,
) -> list[dict]:
    """
    Load the persisted M5.3 output.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"M5.3 output not found: {path}"
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
# SAVE M5.4
# ==========================================================

def save_importance_analytics(
    data: list[dict],
    path: Path,
) -> None:
    """
    Persist M5.4 importance analytics.
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
        "M5.4 — IMPORTANCE ANALYZER TEST"
    )

    print(
        "=" * 65
    )

    # ------------------------------------------------------
    # STEP 1 — LOAD M5.3
    # ------------------------------------------------------

    topics = load_marks_analytics(
        MARKS_ANALYTICS_PATH
    )

    print(
        f"\nM5.3 topics loaded: "
        f"{len(topics)}"
    )

    assert len(topics) > 0

    # ------------------------------------------------------
    # STEP 2 — CREATE ANALYZER
    # ------------------------------------------------------

    analyzer = M5ImportanceAnalyzer(
        topics
    )

    # ------------------------------------------------------
    # STEP 3 — ANALYZE
    # ------------------------------------------------------

    results = analyzer.analyze()

    print(
        f"Topics analyzed: "
        f"{len(results)}"
    )

    assert (
        len(results)
        == len(topics)
    )

    # ------------------------------------------------------
    # STEP 4 — DISPLAY RESULTS
    # ------------------------------------------------------

    print(
        "\n--- TOPIC IMPORTANCE ---"
    )

    for topic in results:

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
            f"  Frequency score: "
            f"{topic['question_frequency_score']}"
        )

        print(
            f"  Recurrence score: "
            f"{topic['paper_recurrence_score']}"
        )

        print(
            f"  Marks score: "
            f"{topic['total_marks_score']}"
        )

        print(
            f"  Long-question score: "
            f"{topic['long_question_score']}"
        )

        print(
            f"  Importance score: "
            f"{topic['importance_score']}"
        )

        print(
            f"  Priority: "
            f"{topic['priority']}"
        )

    # ------------------------------------------------------
    # STEP 5 — CHECK SCORE RANGE
    # ------------------------------------------------------

    for topic in results:

        assert (
            0
            <= topic["importance_score"]
            <= 100
        )

    print(
        "\nImportance score range validation passed."
    )

    # ------------------------------------------------------
    # STEP 6 — CHECK PRIORITY LABEL
    # ------------------------------------------------------

    valid_priorities = {
        "VERY HIGH",
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    for topic in results:

        assert (
            topic["priority"]
            in valid_priorities
        )

    print(
        "Priority label validation passed."
    )

    # ------------------------------------------------------
    # STEP 7 — HYBRID ROUTING CHECK
    # ------------------------------------------------------

    hybrid_topics = [
        topic
        for topic in results
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
        f"Importance score: "
        f"{hybrid['importance_score']}"
    )

    print(
        f"Priority: "
        f"{hybrid['priority']}"
    )

    print(
        f"Questions: "
        f"{hybrid['question_count']}"
    )

    print(
        f"Total marks: "
        f"{hybrid['total_marks']}"
    )

    # Hybrid routing has one 10-mark question.
    assert (
        hybrid["ten_mark_questions"]
        == 1
    )

    # ------------------------------------------------------
    # STEP 8 — CHECK QUESTION PRESERVATION
    # ------------------------------------------------------

    for topic in results:

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
    # STEP 9 — SAVE OUTPUT
    # ------------------------------------------------------

    save_importance_analytics(
        data=results,
        path=IMPORTANCE_ANALYTICS_PATH,
    )

    print(
        "\nM5.4 output saved successfully."
    )

    print(
        "Output file:"
    )

    print(
        IMPORTANCE_ANALYTICS_PATH
    )

    # ------------------------------------------------------
    # STEP 10 — VERIFY OUTPUT
    # ------------------------------------------------------

    assert (
        IMPORTANCE_ANALYTICS_PATH.exists()
    )

    with open(
        IMPORTANCE_ANALYTICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        saved_results = json.load(
            file
        )

    assert (
        len(saved_results)
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
        "M5.4 Importance Analyzer tests "
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