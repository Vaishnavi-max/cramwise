from pathlib import Path

from app.services.llm_analysis.input_service import (
    InputService
)


# ==========================================================
# PROJECT PATH
# ==========================================================

# __file__:
#
# backend/
#   scripts/
#       llm_analysis/
#           test_input_service.py
#
# parents[0] → llm_analysis
# parents[1] → scripts
# parents[2] → backend
#
# Therefore BASE_DIR points to:
#
# C:\Users\vaish\CramWise_vaishi\backend
#
BASE_DIR = Path(__file__).resolve().parents[2]


# ==========================================================
# INPUT FILES
# ==========================================================

# Existing enriched PYQ file.
QUESTIONS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "enriched"
    / "6thsempyqs_2025"
    / "BCS_302_ENDTERM_questions.json"
)


# Existing structured syllabus index.
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

    # Create our input service.
    service = InputService()

    # ------------------------------------------------------
    # 1. LOAD QUESTIONS
    # ------------------------------------------------------

    questions = service.load_questions(
        QUESTIONS_PATH
    )

    # ------------------------------------------------------
    # 2. LOAD SYLLABUS
    # ------------------------------------------------------

    syllabus = service.load_syllabus_index(
        SYLLABUS_PATH
    )

    # ------------------------------------------------------
    # 3. VALIDATE QUESTIONS
    # ------------------------------------------------------

    service.validate_questions(
        questions
    )

    # ------------------------------------------------------
    # 4. VALIDATE SYLLABUS
    # ------------------------------------------------------

    service.validate_syllabus_index(
        syllabus
    )

    # ------------------------------------------------------
    # 5. DISPLAY RESULTS
    # ------------------------------------------------------

    print(
        f"Questions loaded: {len(questions)}"
    )

    print(
        f"Syllabus records loaded: {len(syllabus)}"
    )

    print("\nFirst question:")
    print(questions[0])

    print("\nFirst syllabus record:")
    print(syllabus[0])

    # ------------------------------------------------------
    # SUCCESS MESSAGE
    # ------------------------------------------------------

    print(
        "\nM1 Input Layer validation passed successfully."
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()