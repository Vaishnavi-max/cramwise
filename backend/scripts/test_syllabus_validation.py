import json
from pathlib import Path

from app.validators.syllabus.syllabus_structure_validator import (
    SyllabusStructureValidator,
)


def main():

    # ==========================================================
    # LOAD STRUCTURED SYLLABUS
    # ==========================================================

    input_file = Path(
        "uploads/temp/syllabus/"
        "syllabus_structure.json"
    )

    if not input_file.exists():

        print(
            f"\nERROR: File not found:\n"
            f"{input_file.resolve()}"
        )

        return

    syllabus_data = json.loads(
        input_file.read_text(
            encoding="utf-8"
        )
    )

    # ==========================================================
    # VALIDATE
    # ==========================================================

    print("=" * 80)
    print("M5.2 - SYLLABUS STRUCTURE VALIDATION")
    print("=" * 80)

    result = (
        SyllabusStructureValidator.validate(
            syllabus_data
        )
    )

    # ==========================================================
    # RESULT
    # ==========================================================

    print("\nSTATUS:")

    if result["valid"]:
        print("✓ VALID")
    else:
        print("✗ INVALID")

    # ==========================================================
    # ERRORS
    # ==========================================================

    print("\nERRORS:")

    if result["errors"]:

        for error in result["errors"]:
            print(f"✗ {error}")

    else:

        print("None")

    # ==========================================================
    # WARNINGS
    # ==========================================================

    print("\nWARNINGS:")

    if result["warnings"]:

        for warning in result["warnings"]:
            print(f"⚠ {warning}")

    else:

        print("None")

    # ==========================================================
    # STATS
    # ==========================================================

    print("\nSTATISTICS:")

    for key, value in result["stats"].items():

        print(
            f"{key.capitalize():12}: {value}"
        )

    print("\n" + "=" * 80)
    print("M5.2 VALIDATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()