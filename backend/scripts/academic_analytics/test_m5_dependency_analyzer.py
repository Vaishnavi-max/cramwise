import json
from pathlib import Path

from app.services.academic_analytics.m5_dependency_analyzer import (
    M5DependencyAnalyzer
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


# ==========================================================
# M5.4 INPUT
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
# M5.5 OUTPUT
# ==========================================================

DEPENDENCY_ANALYTICS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
    / "dependency_analytics.json"
)


# ==========================================================
# LOAD M5.4
# ==========================================================

def load_importance_analytics(
    path: Path,
) -> list[dict]:
    """
    Load persisted M5.4 results.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"M5.4 output not found: {path}"
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
# SAVE M5.5
# ==========================================================

def save_dependency_analytics(
    data: list[dict],
    path: Path,
) -> None:
    """
    Save M5.5 dependency analytics.
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
        "M5.5 — DEPENDENCY ANALYZER TEST"
    )

    print(
        "=" * 65
    )

    # ------------------------------------------------------
    # STEP 1 — LOAD M5.4
    # ------------------------------------------------------

    topics = load_importance_analytics(
        IMPORTANCE_ANALYTICS_PATH
    )

    print(
        f"\nM5.4 topics loaded: "
        f"{len(topics)}"
    )

    assert len(topics) > 0

    # ------------------------------------------------------
    # STEP 2 — CREATE ANALYZER
    # ------------------------------------------------------

    analyzer = M5DependencyAnalyzer(
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
    # STEP 4 — DISPLAY SUMMARY
    # ------------------------------------------------------

    print(
        "\n--- DEPENDENCY SUMMARY ---"
    )

    unresolved_total = 0

    for topic in results:

        unresolved_total += (
            topic[
                "unresolved_prerequisite_count"
            ]
        )

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
            f"  Importance: "
            f"{topic['importance_score']}"
        )

        print(
            f"  Priority: "
            f"{topic['priority']}"
        )

        print(
            f"  Prerequisites: "
            f"{topic['prerequisites']}"
        )

        print(
            f"  Unresolved prerequisites: "
            f"{topic['unresolved_prerequisites']}"
        )

        print(
            f"  Dependent topics: "
            f"{topic['dependent_topics']}"
        )

        print(
            f"  Dependency depth: "
            f"{topic['dependency_depth']}"
        )

        print(
            f"  Is prerequisite: "
            f"{topic['is_prerequisite']}"
        )

    print(
        f"\nTotal unresolved prerequisite "
        f"references: {unresolved_total}"
    )

    # ------------------------------------------------------
    # STEP 5 — HYBRID ROUTING CHECK
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
        f"Topic ID: "
        f"{hybrid['topic_id']}"
    )

    print(
        f"Prerequisites: "
        f"{hybrid['prerequisites']}"
    )

    print(
        f"Unresolved prerequisites: "
        f"{hybrid['unresolved_prerequisites']}"
    )

    print(
        f"Dependency depth: "
        f"{hybrid['dependency_depth']}"
    )

    # Hybrid Routing should currently depend on
    # Proactive vs Reactive Routing.

    assert (
        "BCS302_U2_T01_S02"
        in hybrid["prerequisites"]
    )

    assert (
        hybrid["prerequisite_count"]
        >= 1
    )

    # ------------------------------------------------------
    # STEP 6 — REVERSE DEPENDENCY CHECK
    # ------------------------------------------------------

    prerequisite_topics = [
        topic
        for topic in results
        if (
            topic["topic_id"]
            == "BCS302_U2_T01_S02"
        )
    ]

    assert len(
        prerequisite_topics
    ) == 1

    prerequisite = (
        prerequisite_topics[0]
    )

    print(
        "\n--- REVERSE DEPENDENCY CHECK ---"
    )

    print(
        f"Topic: "
        f"{prerequisite['topic_id']}"
    )

    print(
        f"Dependent topics: "
        f"{prerequisite['dependent_topics']}"
    )

    assert (
        "BCS302_U2_T01_S05"
        in prerequisite[
            "dependent_topics"
        ]
    )

    assert (
        prerequisite[
            "is_prerequisite"
        ]
        is True
    )

    # ------------------------------------------------------
    # STEP 7 — VALIDATE COUNTS
    # ------------------------------------------------------

    for topic in results:

        assert (
            topic[
                "prerequisite_count"
            ]
            == len(
                topic[
                    "prerequisites"
                ]
            )
        )

        assert (
            topic[
                "unresolved_prerequisite_count"
            ]
            == len(
                topic[
                    "unresolved_prerequisites"
                ]
            )
        )

        assert (
            topic[
                "dependent_count"
            ]
            == len(
                topic[
                    "dependent_topics"
                ]
            )
        )

    print(
        "\nDependency count validation passed."
    )

    # ------------------------------------------------------
    # STEP 8 — VALIDATE DEPTH
    # ------------------------------------------------------

    for topic in results:

        assert (
            topic[
                "dependency_depth"
            ]
            >= 0
        )

    print(
        "Dependency depth validation passed."
    )

    # ------------------------------------------------------
    # STEP 9 — VALIDATE QUESTIONS
    # ------------------------------------------------------

    for topic in results:

        for question in topic[
            "questions"
        ]:

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
    # STEP 10 — SAVE OUTPUT
    # ------------------------------------------------------

    save_dependency_analytics(
        data=results,
        path=DEPENDENCY_ANALYTICS_PATH,
    )

    print(
        "\nM5.5 output saved successfully."
    )

    print(
        "Output file:"
    )

    print(
        DEPENDENCY_ANALYTICS_PATH
    )

    # ------------------------------------------------------
    # STEP 11 — VERIFY FILE
    # ------------------------------------------------------

    assert (
        DEPENDENCY_ANALYTICS_PATH.exists()
    )

    with open(
        DEPENDENCY_ANALYTICS_PATH,
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
        "M5.5 Dependency Analyzer tests "
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