import json
from pathlib import Path

from app.services.paper_question_parser import (
    PaperQuestionParser,
)


def main():

    # ==========================================================
    # CONFIG
    # ==========================================================

    document_name = "6thsempyqs_2025"

    papers_file = Path(
        "uploads/temp/papers/"
        f"{document_name}/papers.json"
    )

    # ==========================================================
    # CHECK FILE
    # ==========================================================

    if not papers_file.exists():

        print(
            f"\nERROR: papers.json not found:\n"
            f"{papers_file.resolve()}"
        )

        return

    # ==========================================================
    # LOAD PAPERS
    # ==========================================================

    data = json.loads(
        papers_file.read_text(
            encoding="utf-8"
        )
    )

    papers = data.get(
        "papers",
        []
    )

    if not papers:

        print("\nERROR: No papers found.")

        return

    # ==========================================================
    # INITIALIZE PARSER ONCE
    # ==========================================================

    parser = PaperQuestionParser()

    # ==========================================================
    # PROCESS EVERY PAPER
    # ==========================================================

    print("=" * 80)
    print("M3.5 - PARSING ALL PAPERS")
    print("=" * 80)

    print(
        f"\nTotal papers: {len(papers)}\n"
    )

    results = []

    for index, paper in enumerate(
        papers,
        start=1,
    ):

        paper_id = paper["paper_id"]

        pages = paper["pages"]

        print("\n")
        print("=" * 80)

        print(
            f"PAPER {index}/{len(papers)}"
        )

        print(
            f"Paper ID : {paper_id}"
        )

        print(
            f"Subject  : {paper['subject']}"
        )

        print(
            f"Exam     : {paper['exam_type']}"
        )

        print(
            f"Pages    : {pages}"
        )

        print("=" * 80)

        try:

            questions = parser.parse(
                document_name=document_name,
                paper_id=paper_id,
                pages=pages,
            )

            print(
                f"\n✓ SUCCESS"
            )

            print(
                f"Questions parsed: "
                f"{len(questions)}"
            )

            results.append(
                {
                    "paper_id": paper_id,
                    "status": "success",
                    "question_count": len(
                        questions
                    ),
                }
            )

        except Exception as e:

            print(
                f"\n✗ FAILED"
            )

            print(
                f"Error: {e}"
            )

            results.append(
                {
                    "paper_id": paper_id,
                    "status": "failed",
                    "question_count": 0,
                    "error": str(e),
                }
            )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("M3.5 SUMMARY")
    print("=" * 80)

    successful = 0
    failed = 0

    for result in results:

        if result["status"] == "success":

            successful += 1

            print(
                f"✓ {result['paper_id']} "
                f"→ "
                f"{result['question_count']} questions"
            )

        else:

            failed += 1

            print(
                f"✗ {result['paper_id']} "
                f"→ FAILED"
            )

    print("\n" + "-" * 80)

    print(
        f"Successful : {successful}"
    )

    print(
        f"Failed     : {failed}"
    )

    print(
        f"Total      : {len(results)}"
    )

    print("\n" + "=" * 80)
    print("M3.5 COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()