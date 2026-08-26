from pathlib import Path

from app.clients.groq_client import GroqClient

from app.services.llm_analysis.input_service import (
    InputService
)

from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService
)

from app.services.llm_analysis.question_analysis_service import (
    QuestionAnalysisService
)


# ==========================================================
# PROJECT PATH
# ==========================================================

# BASE_DIR points to:
#
# C:\Users\vaish\CramWise_vaishi\backend
#
# because this test file is located at:
#
# backend/scripts/llm_analysis/test_question_analysis.py

BASE_DIR = Path(__file__).resolve().parents[2]


# ==========================================================
# INPUT FILES
# ==========================================================

# ----------------------------------------------------------
# PYQ QUESTIONS
# ----------------------------------------------------------

QUESTIONS_PATH = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "enriched"
    / "6thsempyqs_2025"
    / "BCS_302_ENDTERM_questions.json"
)


# ----------------------------------------------------------
# SYLLABUS INDEX
# ----------------------------------------------------------

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
    # STEP 1 — LOAD DATA
    # ------------------------------------------------------

    input_service = InputService()

    # Load the PYQs that we want to analyze.
    questions = input_service.load_questions(
        QUESTIONS_PATH
    )

    # Load the structured syllabus index.
    syllabus = input_service.load_syllabus_index(
        SYLLABUS_PATH
    )

    # ------------------------------------------------------
    # VALIDATE INPUTS
    # ------------------------------------------------------

    # These validations come from M1.
    #
    # They make sure that the data being passed into
    # the later layers has the expected structure.

    input_service.validate_questions(
        questions
    )

    input_service.validate_syllabus_index(
        syllabus
    )

    # ------------------------------------------------------
    # STEP 2 — CREATE M2 SYLLABUS CATALOG
    # ------------------------------------------------------

    # M2 converts the raw syllabus index into a catalog
    # that can efficiently provide records belonging to
    # a particular subject/unit.

    catalog = SyllabusCatalogService(
        syllabus
    )

    # ------------------------------------------------------
    # STEP 3 — CREATE M3 GROQ CLIENT
    # ------------------------------------------------------

    # M3 is responsible for communicating with Groq.
    #
    # It handles the actual LLM API call and structured
    # JSON generation.

    groq_client = GroqClient()

    # ------------------------------------------------------
    # STEP 4 — CREATE M4 QUESTION ANALYSIS SERVICE
    # ------------------------------------------------------

    # M4 combines:
    #
    #   M2 → syllabus candidates
    #   M3 → LLM analysis
    #
    # to understand what syllabus record the question
    # belongs to and what its dependencies are.

    service = QuestionAnalysisService(
        catalog=catalog,
        groq_client=groq_client,
    )

    # ------------------------------------------------------
    # STEP 5 — SELECT ONE REAL QUESTION
    # ------------------------------------------------------

    # We specifically select the hybrid routing question.
    #
    # This is a useful test because it should map to:
    #
    #   Network Protocols
    #   Hybrid routing protocols

    target_question = next(
        question
        for question in questions
        if (
            "hybrid routing protocols"
            in question["text"].lower()
        )
    )

    # ------------------------------------------------------
    # DISPLAY INPUT QUESTION
    # ------------------------------------------------------

    print(
        "\nQUESTION"
    )

    print(
        target_question["text"]
    )

    print(
        f"\nSubject: "
        f"{target_question['subject_code']}"
    )

    print(
        f"Unit: "
        f"{target_question['unit']}"
    )

    # ------------------------------------------------------
    # STEP 6 — ANALYZE QUESTION
    # ------------------------------------------------------

    print(
        "\nSending question to LLM..."
    )

    result = service.analyze(
        target_question
    )

    # ------------------------------------------------------
    # STEP 7 — DISPLAY RESULT
    # ------------------------------------------------------

    print(
        "\n========== LLM ANALYSIS =========="
    )

    # IMPORTANT:
    #
    # QuestionAnalysisService.analyze()
    # now returns a dictionary.
    #
    # Therefore we use:
    #
    #     result["topic_id"]
    #
    # instead of:
    #
    #     result.topic_id

    print(
        f"Topic ID: "
        f"{result['topic_id']}"
    )

    print(
        f"Topic: "
        f"{result['topic']}"
    )

    print(
        f"Subtopic: "
        f"{result['subtopic']}"
    )

    print(
        f"Independent: "
        f"{result['is_independent']}"
    )

    print(
        f"Prerequisites: "
        f"{result['prerequisites']}"
    )

    print(
        f"Evidence: "
        f"{result['evidence']}"
    )

    print(
        "\nM4 single-question analysis "
        "completed successfully."
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()