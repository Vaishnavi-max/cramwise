import json
from pathlib import Path

from app.services.syllabus_topic_service import (
    SyllabusTopicService,
)


def main():

    # ==========================================================
    # INPUT
    # ==========================================================

    input_file = Path(
        "uploads/temp/syllabus/"
        "syllabus_raw.json"
    )

    # ==========================================================
    # OUTPUT
    # ==========================================================

    output_file = Path(
        "uploads/temp/syllabus/"
        "syllabus_structure.json"
    )

    # ==========================================================
    # LOAD RAW SYLLABUS
    # ==========================================================

    if not input_file.exists():

        print(
            f"\nERROR: Input not found:\n"
            f"{input_file.resolve()}"
        )

        return

    syllabus_data = json.loads(
        input_file.read_text(
            encoding="utf-8"
        )
    )

    print("=" * 80)
    print("M5.2 - ALL SYLLABUS TOPIC STRUCTURING")
    print("=" * 80)

    print(
        f"\nCourses found: "
        f"{len(syllabus_data)}"
    )

    # ==========================================================
    # RUN
    # ==========================================================

    service = SyllabusTopicService()

    structured = service.structure_all(
        syllabus_data=syllabus_data,
        output_file=output_file,
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("\n" + "=" * 80)
    print("M5.2 SUMMARY")
    print("=" * 80)

    total_units = 0

    for course in structured:

        unit_count = len(
            course.get(
                "units",
                []
            )
        )

        total_units += unit_count

        print(
            f"{course['course_code']} "
            f"→ {unit_count} units"
        )

    print(
        f"\nTotal structured units: "
        f"{total_units}"
    )

    print(
        f"\nSaved to:\n"
        f"{output_file.resolve()}"
    )


if __name__ == "__main__":
    main()