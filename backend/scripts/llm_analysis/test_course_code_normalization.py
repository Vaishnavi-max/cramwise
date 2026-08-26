from pathlib import Path

from app.services.llm_analysis.input_service import InputService
from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService
)


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SYLLABUS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "syllabus"
    / "syllabus_index.json"
)


# ==========================================================
# TEST
# ==========================================================

def main():

    # ------------------------------------------------------
    # LOAD SYLLABUS
    # ------------------------------------------------------

    input_service = InputService()

    syllabus = input_service.load_syllabus_index(
        SYLLABUS_PATH
    )

    catalog = SyllabusCatalogService(
        syllabus
    )

    # ------------------------------------------------------
    # TEST 1 — NORMALIZATION
    # ------------------------------------------------------

    assert (
        catalog.normalize_course_code("HMC-306")
        == "HMC306"
    )

    assert (
        catalog.normalize_course_code("HMC 306")
        == "HMC306"
    )

    assert (
        catalog.normalize_course_code("HMC306")
        == "HMC306"
    )

    print("Course-code normalization passed.")

    # ------------------------------------------------------
    # TEST 2 — HMC-306 UNIT 1
    # ------------------------------------------------------

    records = catalog.get_unit_catalog(
        "HMC-306",
        1
    )

    print(
        f"HMC-306 Unit 1 records: {len(records)}"
    )

    assert len(records) > 0

    print("\nFirst HMC-306 Unit 1 record:")

    print(records[0])

    # ------------------------------------------------------
    # TEST 3 — HMC 306 SHOULD RETURN SAME RECORDS
    # ------------------------------------------------------

    records_with_space = (
        catalog.get_unit_catalog(
            "HMC 306",
            1
        )
    )

    assert (
        len(records)
        == len(records_with_space)
    )

    print(
        "\nHMC-306 and HMC 306 lookup "
        "returned the same number of records."
    )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print(
        "\nM2 course-code normalization "
        "tests passed successfully."
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()