import json
from pathlib import Path

from app.validators.question_output_validator import (
    QuestionOutputValidator,
)


def main():

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    document_name = "6thsempyqs_2025"

    parsed_dir = (
        Path("uploads/temp/parsed")
        / document_name
    )

    # ==========================================================
    # CHECK DIRECTORY
    # ==========================================================

    if not parsed_dir.exists():

        print(
            f"\nERROR: Parsed directory not found:\n"
            f"{parsed_dir.resolve()}"
        )

        return

    # ==========================================================
    # ONLY PAPER-LEVEL JSON FILES
    # ==========================================================

    paper_files = sorted(
        parsed_dir.glob(
            "*_questions.json"
        )
    )

    # Remove old page-wise files
    paper_files = [
        file
        for file in paper_files
        if not file.name.startswith("page_")
    ]

    if not paper_files:

        print(
            "\nERROR: No paper question files found."
        )

        return

    print("=" * 80)
    print("M3.6 - QUESTION OUTPUT VALIDATION")
    print("=" * 80)

    print(
        f"\nFound {len(paper_files)} paper files."
    )

    passed = 0
    failed = 0

    # ==========================================================
    # VALIDATE EACH PAPER
    # ==========================================================

    for json_file in paper_files:

        print("\n" + "-" * 80)

        print(
            f"Paper: {json_file.stem}"
        )

        # ------------------------------------------------------
        # Load JSON
        # ------------------------------------------------------

        try:

            data = json.loads(
                json_file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as e:

            print(
                "\n❌ INVALID JSON FILE"
            )

            print(e)

            failed += 1

            continue

        # ------------------------------------------------------
        # Determine exam type from filename
        # ------------------------------------------------------

        filename = json_file.stem.upper()

        if "MIDTERM" in filename:

            exam_type = "MIDTERM"

        elif "ENDTERM" in filename:

            exam_type = "ENDTERM"

        else:

            print(
                "\n❌ Could not determine exam type."
            )

            failed += 1

            continue

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        report = (
            QuestionOutputValidator.validate(
                data,
                exam_type,
            )
        )

        # ------------------------------------------------------
        # Result
        # ------------------------------------------------------

        if report["valid"]:

            print(
                "\n✓ VALID"
            )

            passed += 1

        else:

            print(
                "\n✗ INVALID"
            )

            failed += 1

        # ------------------------------------------------------
        # Show errors
        # ------------------------------------------------------

        if report["errors"]:

            print("\nErrors:")

            for error in report["errors"]:

                print(
                    f"  ❌ {error}"
                )

        # ------------------------------------------------------
        # Show warnings
        # ------------------------------------------------------

        if report["warnings"]:

            print("\nWarnings:")

            for warning in report["warnings"]:

                print(
                    f"  ⚠ {warning}"
                )

        # ------------------------------------------------------
        # Show basic structure
        # ------------------------------------------------------

        print(
            f"\nTotal parsed objects: "
            f"{len(data)}"
        )

    # ==========================================================
    # FINAL SUMMARY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("M3.6 VALIDATION SUMMARY")
    print("=" * 80)

    print(
        f"\nPassed : {passed}"
    )

    print(
        f"Failed : {failed}"
    )

    print(
        f"Total  : {len(paper_files)}"
    )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()