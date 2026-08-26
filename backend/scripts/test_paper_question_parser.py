import json
from pathlib import Path

from app.services.paper_question_parser import (
    PaperQuestionParser,
)


def main():

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    document_name = "6thsempyqs_2025"

    paper_id = "BCS_304_ENDTERM"

    # ==========================================================
    # LOAD PAPERS.JSON
    # ==========================================================

    papers_file = Path(
        "uploads/temp/papers/"
        "6thsempyqs_2025/papers.json"
    )

    if not papers_file.exists():

        print(
            "\nERROR: papers.json not found:"
        )

        print(
            papers_file.resolve()
        )

        return

    data = json.loads(
        papers_file.read_text(
            encoding="utf-8"
        )
    )

    # ==========================================================
    # FIND PAPER
    # ==========================================================

    selected_paper = None

    for paper in data.get(
        "papers",
        [],
    ):

        if paper.get(
            "paper_id"
        ) == paper_id:

            selected_paper = paper

            break

    if selected_paper is None:

        print(
            f"\nERROR: Paper not found: "
            f"{paper_id}"
        )

        return

    # ==========================================================
    # DISPLAY PAPER
    # ==========================================================

    print("=" * 80)
    print("M3 - PAPER QUESTION PARSER TEST")
    print("=" * 80)

    print(
        f"\nPaper ID     : "
        f"{selected_paper['paper_id']}"
    )

    print(
        f"Subject      : "
        f"{selected_paper['subject']}"
    )

    print(
        f"Exam Type    : "
        f"{selected_paper['exam_type']}"
    )

    print(
        f"Pages        : "
        f"{selected_paper['pages']}"
    )

    # ==========================================================
    # PARSE
    # ==========================================================

    parser = PaperQuestionParser()

    questions = parser.parse(
        document_name=document_name,
        paper_id=paper_id,
        pages=selected_paper["pages"],
    )

    # ==========================================================
    # OUTPUT
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("FINAL QUESTIONS")
    print("=" * 80)

    print(
        f"\nTotal questions: "
        f"{len(questions)}\n"
    )

    for question in questions:
        print("-" * 80)

        # Support both dictionary representations and object instances safely
        q_num = question.get("question_number") if isinstance(question, dict) else getattr(question, "question_number", "")
        q_sub = question.get("sub_question") or question.get("part") if isinstance(question, dict) else getattr(question, "sub_question", "")
        q_marks = question.get("marks") or question.get("question_marks") if isinstance(question, dict) else getattr(question, "marks", "")
        q_text = question.get("text", "") if isinstance(question, dict) else getattr(question, "text", "")


        print(
            f"Question Number : "
            f"{q_num}"
        )

        print(
            f"Part            : "
            f"{q_sub}"
        )

        print(
            f"Marks           : "
            f"{q_marks}"
        )

        print(
            f"Text            : "
            f"{q_text}"
        )

    print("\n")
    print("=" * 80)
    print("M3 PAPER QUESTION PARSER TEST COMPLETED")
    print("=" * 80)

    
if __name__ == "__main__":
    main()