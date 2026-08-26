import json
import time
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
# PATHS
# ==========================================================

# Points to:
#
# C:\Users\vaish\CramWise_vaishi\backend

BASE_DIR = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------
# ENRICHED PYQ DIRECTORY
# ----------------------------------------------------------

QUESTIONS_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "enriched"
    / "6thsempyqs_2025"
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


# ----------------------------------------------------------
# OUTPUT DIRECTORY
# ----------------------------------------------------------

# Every PYQ paper will get its own analysis JSON here.
#
# Example:
#
# uploads/temp/analyzed/6thsempyqs_2025/
#
#     BCS_302_ENDTERM_analysis.json
#     BCS_302_MIDTERM_analysis.json
#     ...
#
#     analysis_summary.json

OUTPUT_DIR = (
    BASE_DIR
    / "uploads"
    / "temp"
    / "analyzed"
    / "6thsempyqs_2025"
)


# ==========================================================
# SETTINGS
# ==========================================================

# Wait between successful Groq calls.
#
# This helps avoid hitting Groq's TPM/rate limits too
# aggressively while processing many questions.

DELAY_BETWEEN_CALLS = 1.0


# ==========================================================
# JSON HELPERS
# ==========================================================

def load_json(path: Path):
    """
    Load a JSON file and return the Python object.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def save_json(
    path: Path,
    data,
):
    """
    Save data as nicely formatted JSON.
    """

    # Make sure the output directory exists.
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
# QUESTION ID
# ==========================================================

def get_question_id(question: dict) -> str:
    """
    Create a stable ID for a question.

    We use:

        paper_id
        +
        question number
        +
        sub-question

    Examples:

        BCS_302_ENDTERM_Q5

        BCS_302_ENDTERM_Q1_a

    This lets us recognize questions when the script
    is restarted.
    """

    paper_id = question.get(
        "paper_id",
        "UNKNOWN",
    )

    question_number = question.get(
        "question_number",
        "UNKNOWN",
    )

    sub_question = question.get(
        "sub_question"
    )

    if sub_question:

        return (
            f"{paper_id}"
            f"_Q{question_number}"
            f"_{sub_question}"
        )

    return (
        f"{paper_id}"
        f"_Q{question_number}"
    )


# ==========================================================
# EXISTING RESULTS
# ==========================================================

def load_existing_results(
    output_path: Path,
) -> dict:
    """
    Load an existing analysis file if it exists.

    If it doesn't exist, return an empty structure.

    This is the core of the resume mechanism.
    """

    if not output_path.exists():

        return {
            "source_file": None,
            "question_count": 0,
            "successful": 0,
            "failed": 0,
            "questions": [],
        }

    print(
        f"Existing result found: "
        f"{output_path.name}"
    )

    existing = load_json(
        output_path
    )

    return existing


# ==========================================================
# BUILD CACHE
# ==========================================================

def build_success_cache(
    existing_result: dict,
) -> dict:
    """
    Convert previously successful analyses into a dictionary.

    Example:

        {
            "BCS_302_ENDTERM_Q5": {...},
            "BCS_302_ENDTERM_Q6": {...}
        }

    Only SUCCESSFUL analyses are cached.

    Failed questions are deliberately NOT cached because
    we want them to be retried on the next run.
    """

    cache = {}

    for item in existing_result.get(
        "questions",
        [],
    ):

        analysis = item.get(
            "analysis"
        )

        question = item.get(
            "question"
        )

        # No analysis means the previous attempt failed.
        if not analysis:
            continue

        if not question:
            continue

        question_id = get_question_id(
            question
        )

        cache[
            question_id
        ] = item

    return cache


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 65)
    print("CramWise M4 — Resume-Safe Batch Analysis")
    print("=" * 65)

    # ------------------------------------------------------
    # M1 — INPUT
    # ------------------------------------------------------

    input_service = InputService()

    # Load the syllabus index.
    syllabus = (
        input_service.load_syllabus_index(
            SYLLABUS_PATH
        )
    )

    # Validate syllabus structure.
    input_service.validate_syllabus_index(
        syllabus
    )

    print(
        f"\nSyllabus records loaded: "
        f"{len(syllabus)}"
    )

    # ------------------------------------------------------
    # M2 — SYLLABUS CATALOG
    # ------------------------------------------------------

    catalog = SyllabusCatalogService(
        syllabus
    )

    print(
        "M2 syllabus catalog ready."
    )

    # ------------------------------------------------------
    # M3 — GROQ
    # ------------------------------------------------------

    groq_client = GroqClient()

    print(
        f"M3 Groq client ready: "
        f"{groq_client.model}"
    )

    # ------------------------------------------------------
    # M4 — QUESTION ANALYSIS
    # ------------------------------------------------------

    analysis_service = (
        QuestionAnalysisService(
            catalog=catalog,
            groq_client=groq_client,
        )
    )

    print(
        "M4 question analysis service ready."
    )

    # ------------------------------------------------------
    # FIND PYQ FILES
    # ------------------------------------------------------

    question_files = sorted(
        QUESTIONS_DIR.glob(
            "*_questions.json"
        )
    )

    if not question_files:

        raise FileNotFoundError(
            "No enriched question files found."
        )

    print(
        f"\nPYQ files found: "
        f"{len(question_files)}"
    )

    # ------------------------------------------------------
    # GLOBAL COUNTERS
    # ------------------------------------------------------

    total_questions = 0
    total_successful = 0
    total_failed = 0
    total_skipped = 0

    # ------------------------------------------------------
    # PROCESS EACH PAPER
    # ------------------------------------------------------

    for question_file in question_files:

        print("\n" + "=" * 65)

        print(
            f"PROCESSING: "
            f"{question_file.name}"
        )

        # --------------------------------------------------
        # LOAD QUESTIONS
        # --------------------------------------------------

        questions = (
            input_service.load_questions(
                question_file
            )
        )

        input_service.validate_questions(
            questions
        )

        print(
            f"Questions: "
            f"{len(questions)}"
        )

        total_questions += len(
            questions
        )

        # --------------------------------------------------
        # OUTPUT PATH
        # --------------------------------------------------

        output_name = (
            question_file.stem
            .replace(
                "_questions",
                "_analysis",
            )
            + ".json"
        )

        output_path = (
            OUTPUT_DIR
            / output_name
        )

        # --------------------------------------------------
        # LOAD PREVIOUS RESULTS
        # --------------------------------------------------

        existing_result = (
            load_existing_results(
                output_path
            )
        )

        success_cache = (
            build_success_cache(
                existing_result
            )
        )

        print(
            f"Previously successful: "
            f"{len(success_cache)}"
        )

        # --------------------------------------------------
        # CREATE RESULT CONTAINER
        # --------------------------------------------------

        paper_result = {
            "source_file": question_file.name,
            "question_count": len(questions),
            "successful": 0,
            "failed": 0,
            "questions": [],
        }

        # --------------------------------------------------
        # PROCESS QUESTIONS
        # --------------------------------------------------

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question_id = (
                get_question_id(
                    question
                )
            )

            print(
                f"\n[{index}/{len(questions)}] "
                f"{question_id}"
            )

            # ==================================================
            # CACHE CHECK
            # ==================================================

            if question_id in success_cache:

                print(
                    "  ↻ Already analyzed — "
                    "SKIPPING Groq call"
                )

                # Reuse the previous successful result.
                paper_result[
                    "questions"
                ].append(
                    success_cache[
                        question_id
                    ]
                )

                paper_result[
                    "successful"
                ] += 1

                total_successful += 1
                total_skipped += 1

                continue

            # ==================================================
            # NEW / FAILED QUESTION
            # ==================================================

            print(
                "  → Sending to Groq..."
            )

            print(
                f"  Question: "
                f"{question['text']}"
            )

            try:

                # --------------------------------------------------
                # CALL M4
                # --------------------------------------------------

                analysis = (
                    analysis_service.analyze(
                        question
                    )
                )

                # --------------------------------------------------
                # STORE SUCCESS
                # --------------------------------------------------

                # IMPORTANT:
                #
                # QuestionAnalysisService.analyze()
                # now returns a DICTIONARY.
                #
                # Therefore we DO NOT use:
                #
                #     analysis.model_dump()
                #
                # because dictionaries don't have model_dump().
                #
                # We directly store:
                #
                #     analysis

                result = {
                    "question": question,
                    "analysis": analysis,
                }

                paper_result[
                    "questions"
                ].append(
                    result
                )

                paper_result[
                    "successful"
                ] += 1

                total_successful += 1

                print(
                    "  ✓ SUCCESS"
                )

                # --------------------------------------------------
                # DISPLAY CANONICAL SYLLABUS INFORMATION
                # --------------------------------------------------

                print(
                    f"  Topic ID: "
                    f"{analysis['topic_id']}"
                )

                print(
                    f"  Topic: "
                    f"{analysis['topic']}"
                )

                print(
                    f"  Subtopic: "
                    f"{analysis['subtopic']}"
                )

                print(
                    f"  Independent: "
                    f"{analysis['is_independent']}"
                )

                print(
                    f"  Prerequisites: "
                    f"{analysis['prerequisites']}"
                )

                # --------------------------------------------------
                # SAVE IMMEDIATELY AFTER SUCCESS
                # --------------------------------------------------

                # This is important.
                #
                # If the program crashes after this question,
                # we don't lose the work already completed.

                save_json(
                    output_path,
                    paper_result,
                )

                print(
                    "  ✓ Saved immediately"
                )

                # --------------------------------------------------
                # WAIT BEFORE NEXT API CALL
                # --------------------------------------------------

                time.sleep(
                    DELAY_BETWEEN_CALLS
                )

            except Exception as exc:

                # --------------------------------------------------
                # STORE FAILURE
                # --------------------------------------------------

                failed_result = {
                    "question": question,
                    "analysis": None,
                    "error": str(exc),
                }

                paper_result[
                    "questions"
                ].append(
                    failed_result
                )

                paper_result[
                    "failed"
                ] += 1

                total_failed += 1

                print(
                    f"  ✗ FAILED: "
                    f"{exc}"
                )

                # --------------------------------------------------
                # SAVE EVEN AFTER FAILURE
                # --------------------------------------------------

                # We save the failure so we don't lose progress.
                #
                # Because analysis == None, this question will
                # NOT be added to the success cache on the next
                # run and will therefore be retried.

                save_json(
                    output_path,
                    paper_result,
                )

        # --------------------------------------------------
        # FINAL SAVE FOR THIS PAPER
        # --------------------------------------------------

        save_json(
            output_path,
            paper_result,
        )

        print(
            "\nSaved paper results:"
        )

        print(
            output_path
        )

        print(
            f"Successful: "
            f"{paper_result['successful']}"
        )

        print(
            f"Failed: "
            f"{paper_result['failed']}"
        )

    # ======================================================
    # GLOBAL SUMMARY
    # ======================================================

    summary = {
        "dataset": "6thsempyqs_2025",
        "total_questions": total_questions,
        "successful": total_successful,
        "failed": total_failed,
        "skipped_from_cache": total_skipped,
    }

    summary_path = (
        OUTPUT_DIR
        / "analysis_summary.json"
    )

    save_json(
        summary_path,
        summary,
    )

    # ======================================================
    # FINAL REPORT
    # ======================================================

    print("\n" + "=" * 65)
    print("M4 BATCH COMPLETE")
    print("=" * 65)

    print(
        f"Total questions: "
        f"{total_questions}"
    )

    print(
        f"Successful analyses: "
        f"{total_successful}"
    )

    print(
        f"Failed analyses: "
        f"{total_failed}"
    )

    print(
        f"Skipped from cache: "
        f"{total_skipped}"
    )

    print(
        f"\nResults directory:"
    )

    print(
        OUTPUT_DIR
    )

    print(
        f"\nSummary:"
    )

    print(
        summary_path
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()