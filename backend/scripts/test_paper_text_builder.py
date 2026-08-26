import json
from pathlib import Path

from app.services.paper_text_builder import PaperTextBuilder


def main():

    # ==========================================================
    # PAPERS JSON
    # ==========================================================

    papers_file = Path(
        "uploads/temp/papers/"
        "6thsempyqs_2025/papers.json"
    )

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

        print(
            "\nERROR: No papers found."
        )

        return

    # ==========================================================
    # TEST FIRST PAPER WITH MULTIPLE PAGES
    # ==========================================================

    selected_paper = None

    for paper in papers:

        if len(paper["pages"]) > 1:

            selected_paper = paper
            break

    if selected_paper is None:

        print(
            "\nERROR: No multi-page paper found."
        )

        return

    # ==========================================================
    # BUILD TEXT
    # ==========================================================

    print("=" * 80)
    print("M3 - PAPER TEXT BUILDER TEST")
    print("=" * 80)

    print(
        f"\nPaper ID : "
        f"{selected_paper['paper_id']}"
    )

    print(
        f"Subject  : "
        f"{selected_paper['subject']}"
    )

    print(
        f"Pages    : "
        f"{selected_paper['pages']}"
    )

    builder = PaperTextBuilder()

    combined_text = builder.build(
        document_name=data["document"],
        pages=selected_paper["pages"],
    )

    # ==========================================================
    # DISPLAY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("COMBINED OCR TEXT")
    print("=" * 80)

    print(combined_text)

    print("\n")
    print("=" * 80)
    print("M3 TEXT BUILDER TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()