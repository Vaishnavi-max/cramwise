from pathlib import Path

from app.services.academic_analytics.m5_result_loader import (
    M5ResultLoader
)


# ==========================================================
# PROJECT PATH
# ==========================================================

# This resolves to:
#
# C:\Users\vaish\CramWise_vaishi\backend

BASE_DIR = Path(
    __file__
).resolve().parents[2]


# ==========================================================
# M4 OUTPUT DIRECTORY
# ==========================================================

ANALYSIS_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analyzed"
    / "6thsempyqs_2025"
)


# ==========================================================
# TEST
# ==========================================================

def main():

    print(
        "=" * 60
    )

    print(
        "M5.1 — RESULT LOADER TEST"
    )

    print(
        "=" * 60
    )

    # ------------------------------------------------------
    # CREATE LOADER
    # ------------------------------------------------------

    loader = M5ResultLoader(
        ANALYSIS_DIR
    )

    # ------------------------------------------------------
    # TEST 1 — FILE COUNT
    # ------------------------------------------------------

    file_count = (
        loader.get_file_count()
    )

    print(
        f"\nAnalysis files found: "
        f"{file_count}"
    )

    assert file_count > 0, (
        "No M4 analysis files found."
    )

    # ------------------------------------------------------
    # TEST 2 — LOAD ALL RESULTS
    # ------------------------------------------------------

    results = (
        loader.load_all()
    )

    print(
        f"Successful M4 results loaded: "
        f"{len(results)}"
    )

    # We currently expect 152 successful
    # analyses based on the M4 batch run.

    assert len(results) == 152, (
        f"Expected 152 successful analyses, "
        f"but loaded {len(results)}."
    )

    # ------------------------------------------------------
    # TEST 3 — CHECK FIRST RESULT
    # ------------------------------------------------------

    first = results[0]

    print(
        "\n--- FIRST RESULT ---"
    )

    print(
        "Question:"
    )

    print(
        first["question"]
    )

    print(
        "\nAnalysis:"
    )

    print(
        first["analysis"]
    )

    # ------------------------------------------------------
    # TEST 4 — STRUCTURE VALIDATION
    # ------------------------------------------------------

    assert (
        "question"
        in first
    )

    assert (
        "analysis"
        in first
    )

    # ------------------------------------------------------
    # TEST 5 — ANALYSIS VALIDATION
    # ------------------------------------------------------

    analysis = first[
        "analysis"
    ]

    required_fields = [
        "topic_id",
        "topic",
        "subtopic",
        "is_independent",
        "prerequisites",
        "evidence",
    ]

    for field in required_fields:

        assert field in analysis, (
            f"Missing M4 field: {field}"
        )

    print(
        "\nM4 analysis structure "
        "validation passed."
    )

    # ------------------------------------------------------
    # TEST 6 — NO FAILED RESULTS
    # ------------------------------------------------------

    for result in results:

        assert (
            result["analysis"]
            is not None
        )

    print(
        "No failed M4 analyses "
        "entered the M5 dataset."
    )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "M5.1 Result Loader tests "
        "passed successfully."
    )

    print(
        "=" * 60
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()