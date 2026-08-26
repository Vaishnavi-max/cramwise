import json
from pathlib import Path

from app.services.academic_analytics.m5_priority_analyzer import (
    M5PriorityAnalyzer
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
# ANALYTICS DIRECTORY
# ==========================================================

ANALYTICS_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analytics"
    / "6thsempyqs_2025"
)


# ==========================================================
# INPUT FILES
# ==========================================================

IMPORTANCE_PATH = (
    ANALYTICS_DIR
    / "importance_analytics.json"
)

DEPENDENCY_PATH = (
    ANALYTICS_DIR
    / "dependency_analytics.json"
)


# ==========================================================
# OUTPUT FILE
# ==========================================================

OUTPUT_PATH = (
    ANALYTICS_DIR
    / "priority_analytics.json"
)


# ==========================================================
# LOAD JSON
# ==========================================================

def load_json(
    path: Path,
):
    """
    Load a JSON file from disk.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ==========================================================
# SAVE JSON
# ==========================================================

def save_json(
    data,
    path: Path,
):
    """
    Save the final M5.6 output.
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
        "M5.6 — FINAL PRIORITY ANALYZER TEST"
    )

    print(
        "=" * 65
    )

    # ------------------------------------------------------
    # STEP 1 — LOAD M5.4
    # ------------------------------------------------------

    importance = load_json(
        IMPORTANCE_PATH
    )

    print(
        f"\nImportance topics loaded: "
        f"{len(importance)}"
    )

    # ------------------------------------------------------
    # STEP 2 — LOAD M5.5
    # ------------------------------------------------------

    dependency = load_json(
        DEPENDENCY_PATH
    )

    print(
        f"Dependency topics loaded: "
        f"{len(dependency)}"
    )

    # ------------------------------------------------------
    # STEP 3 — BASIC VALIDATION
    # ------------------------------------------------------

    assert (
        len(importance)
        == 100
    ), (
        "Expected 100 importance topics."
    )

    assert (
        len(dependency)
        == 100
    ), (
        "Expected 100 dependency topics."
    )

    # ------------------------------------------------------
    # STEP 4 — CREATE ANALYZER
    # ------------------------------------------------------

    analyzer = M5PriorityAnalyzer(
        importance_analytics=importance,
        dependency_analytics=dependency,
    )

    print(
        "\nM5.4 + M5.5 alignment validation passed."
    )

    # ------------------------------------------------------
    # STEP 5 — RUN M5.6
    # ------------------------------------------------------

    results = analyzer.analyze()

    print(
        f"\nFinal topics generated: "
        f"{len(results)}"
    )

    assert (
        len(results)
        == len(importance)
    )

    # ------------------------------------------------------
    # STEP 6 — CHECK STUDY ORDER
    # ------------------------------------------------------

    study_orders = [
        item["study_order"]
        for item in results
    ]

    expected_orders = list(
        range(
            1,
            len(results) + 1,
        )
    )

    assert (
        sorted(study_orders)
        == expected_orders
    ), (
        "Study orders are not unique "
        "or complete."
    )

    print(
        "Study order validation passed."
    )

    # ------------------------------------------------------
    # STEP 7 — CHECK FINAL OUTPUT FIELDS
    # ------------------------------------------------------

    required_fields = [
        "topic_id",
        "topic",
        "subtopic",
        "unit",
        "importance_score",
        "final_priority",
        "prerequisites",
        "dependency_depth",
        "study_order",
        "study_reason",
    ]

    for item in results:

        for field in required_fields:

            assert (
                field in item
            ), (
                f"Missing field "
                f"'{field}' in "
                f"{item['topic_id']}"
            )

    print(
        "Required field validation passed."
    )

    # ------------------------------------------------------
    # STEP 8 — ENSURE INTERNAL SCORE IS NOT EXPOSED
    # ------------------------------------------------------

    for item in results:

        assert (
            "_final_score"
            not in item
        ), (
            "Internal final score should "
            "not appear in final JSON."
        )

    print(
        "Clean output structure validation passed."
    )

    # ------------------------------------------------------
    # STEP 9 — CHECK PRIORITY LABELS
    # ------------------------------------------------------

    valid_priorities = {
        "VERY HIGH",
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    for item in results:

        assert (
            item[
                "final_priority"
            ]
            in valid_priorities
        )

    print(
        "Priority label validation passed."
    )

    # ------------------------------------------------------
    # STEP 10 — CHECK HYBRID ROUTING
    # ------------------------------------------------------

    hybrid = next(
        item
        for item in results
        if (
            item["topic_id"]
            == "BCS302_U2_T01_S05"
        )
    )

    print(
        "\n--- HYBRID ROUTING CHECK ---"
    )

    print(
        f"Topic: "
        f"{hybrid['topic']}"
    )

    print(
        f"Subtopic: "
        f"{hybrid['subtopic']}"
    )

    print(
        f"Importance score: "
        f"{hybrid['importance_score']}"
    )

    print(
        f"Final priority: "
        f"{hybrid['final_priority']}"
    )

    print(
        f"Prerequisites: "
        f"{hybrid['prerequisites']}"
    )

    print(
        f"Dependency depth: "
        f"{hybrid['dependency_depth']}"
    )

    print(
        f"Study order: "
        f"{hybrid['study_order']}"
    )

    print(
        f"Study reason: "
        f"{hybrid['study_reason']}"
    )

    # Hybrid routing should have the prerequisite:
    #
    # BCS302_U2_T01_S02
    #
    # Proactive vs reactive routing.

    assert (
        "BCS302_U2_T01_S02"
        in hybrid[
            "prerequisites"
        ]
    )

    print(
        "Hybrid prerequisite validation passed."
    )

    # ------------------------------------------------------
    # STEP 11 — PREREQUISITE ORDER CHECK
    # ------------------------------------------------------

    proactive = next(
        item
        for item in results
        if (
            item["topic_id"]
            == "BCS302_U2_T01_S02"
        )
    )

    assert (
        proactive[
            "study_order"
        ]
        <
        hybrid[
            "study_order"
        ]
    ), (
        "Prerequisite must appear before "
        "dependent topic."
    )

    print(
        "Prerequisite-before-dependent "
        "ordering passed."
    )

    # ------------------------------------------------------
    # STEP 12 — CHECK REASONS
    # ------------------------------------------------------

    for item in results:

        assert isinstance(
            item[
                "study_reason"
            ],
            list,
        )

        assert (
            len(
                item[
                    "study_reason"
                ]
            )
            > 0
        )

    print(
        "Study-reason validation passed."
    )

    # ------------------------------------------------------
    # STEP 13 — SAVE OUTPUT
    # ------------------------------------------------------

    save_json(
        data=results,
        path=OUTPUT_PATH,
    )

    print(
        "\nM5.6 output saved to:"
    )

    print(
        OUTPUT_PATH
    )

    assert (
        OUTPUT_PATH.exists()
    )

    # ------------------------------------------------------
    # STEP 14 — RELOAD OUTPUT
    # ------------------------------------------------------

    saved_results = load_json(
        OUTPUT_PATH
    )

    assert (
        len(saved_results)
        == len(results)
    )

    print(
        "Saved JSON validation passed."
    )

    # ------------------------------------------------------
    # STEP 15 — DISPLAY TOP 15
    # ------------------------------------------------------

    print(
        "\n--- TOP 15 RECOMMENDED STUDY ORDER ---"
    )

    for item in results[:15]:

        print(
            f"{item['study_order']:>3}. "
            f"{item['topic_id']} | "
            f"{item['subtopic']} | "
            f"{item['final_priority']} | "
            f"Importance: "
            f"{item['importance_score']}"
        )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print(
        "\n" + "=" * 65
    )

    print(
        "M5.6 Final Priority Analyzer "
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