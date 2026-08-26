from pathlib import Path

from app.services.llm_analysis.input_service import (
    InputService
)

from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService
)


# ==========================================================
# PROJECT PATH
# ==========================================================

# We are running this script from:
#
# backend/
#     scripts/
#         llm_analysis/
#
# parents[2] therefore points to:
#
# backend/
#
BASE_DIR = Path(__file__).resolve().parents[2]


# ==========================================================
# SYLLABUS FILE
# ==========================================================

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
    # STEP 1 — LOAD SYLLABUS
    # ------------------------------------------------------

    input_service = InputService()

    syllabus = input_service.load_syllabus_index(
        SYLLABUS_PATH
    )

    # Validate the raw syllabus before using it.
    input_service.validate_syllabus_index(
        syllabus
    )

    print(
        f"Syllabus records loaded: {len(syllabus)}"
    )

    # ------------------------------------------------------
    # STEP 2 — CREATE CATALOG
    # ------------------------------------------------------

    catalog = SyllabusCatalogService(
        syllabus
    )

    print(
        "Syllabus catalog created successfully."
    )

    # ------------------------------------------------------
    # TEST 1 — GET SUBJECTS
    # ------------------------------------------------------

    print("\n--- TEST 1: SUBJECTS ---")

    subjects = catalog.get_subjects()

    print(
        f"Number of subjects: {len(subjects)}"
    )

    print(
        "Subjects:"
    )

    for subject in subjects:
        print(
            f"  - {subject}"
        )

    # ------------------------------------------------------
    # TEST 2 — GET SUBJECT CATALOG
    # ------------------------------------------------------

    print("\n--- TEST 2: BCS 302 CATALOG ---")

    bcs302_records = (
        catalog.get_subject_catalog(
            "BCS 302"
        )
    )

    print(
        f"BCS 302 records: "
        f"{len(bcs302_records)}"
    )

    # Show first 3 records only so the terminal
    # doesn't become unnecessarily large.
    for record in bcs302_records[:3]:
        print(record)

    # ------------------------------------------------------
    # TEST 3 — GET UNIT CATALOG
    # ------------------------------------------------------

    print("\n--- TEST 3: BCS 302 UNIT 2 ---")

    unit2_records = (
        catalog.get_unit_catalog(
            "BCS 302",
            2
        )
    )

    print(
        f"BCS 302 Unit 2 records: "
        f"{len(unit2_records)}"
    )

    for record in unit2_records[:5]:
        print(record)

    # ------------------------------------------------------
    # TEST 4 — GET ONE RECORD BY ID
    # ------------------------------------------------------

    print("\n--- TEST 4: GET BY ID ---")

    topic = catalog.get_topic(
        "BCS302_U1_T01_S01"
    )

    print(
        "Requested ID:"
    )

    print(
        "BCS302_U1_T01_S01"
    )

    print(
        "Result:"
    )

    print(topic)

    # ------------------------------------------------------
    # TEST 5 — INVALID ID
    # ------------------------------------------------------

    print("\n--- TEST 5: INVALID ID ---")

    invalid_topic = catalog.get_topic(
        "INVALID_ID"
    )

    print(
        f"Result for invalid ID: "
        f"{invalid_topic}"
    )

    # ------------------------------------------------------
    # TEST 6 — GET TOPIC IDS FOR UNIT
    # ------------------------------------------------------

    print("\n--- TEST 6: TOPIC IDS ---")

    unit2_ids = catalog.get_topic_ids(
        "BCS 302",
        2
    )

    print(
        f"Number of Unit 2 IDs: "
        f"{len(unit2_ids)}"
    )

    print(
        "First 5 IDs:"
    )

    for topic_id in unit2_ids[:5]:
        print(
            f"  - {topic_id}"
        )

    # ------------------------------------------------------
    # TEST 7 — CHECK UNIT FILTERING
    # ------------------------------------------------------

    print("\n--- TEST 7: UNIT FILTER CHECK ---")

    wrong_units = [
        record
        for record in unit2_records
        if record["unit_number"] != 2
    ]

    if wrong_units:

        raise AssertionError(
            "Unit filtering failed. "
            "Found records from another unit."
        )

    print(
        "All returned records belong to Unit 2."
    )

    # ------------------------------------------------------
    # TEST 8 — CHECK SUBJECT FILTERING
    # ------------------------------------------------------

    print("\n--- TEST 8: SUBJECT FILTER CHECK ---")

    wrong_subjects = [
        record
        for record in bcs302_records
        if record["course_code"] != "BCS 302"
    ]

    if wrong_subjects:

        raise AssertionError(
            "Subject filtering failed. "
            "Found records from another subject."
        )

    print(
        "All returned records belong to BCS 302."
    )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print(
        "\nM2 Syllabus Catalog tests "
        "passed successfully."
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()