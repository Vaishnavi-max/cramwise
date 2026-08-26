from pathlib import Path
import json

from app.parsers.metadata_extractor import MetadataExtractor
from app.parsers.paper_grouper import PaperGrouper
from app.services.paper_storage import PaperStorage

def main():

    # ==========================================================
    # 1. LOCATION OF YOUR CLEANED OCR PAGES
    # ==========================================================

    cleaned_dir = Path(
        "uploads/temp/cleaned/6thsempyqs_2025"
    )

    if not cleaned_dir.exists():

        print(
            f"\nERROR: Folder not found:\n"
            f"{cleaned_dir.resolve()}"
        )

        return

    # ==========================================================
    # 2. FIND ALL PAGE FILES
    # ==========================================================

    page_files = sorted(
        cleaned_dir.glob("page_*.txt"),
        key=lambda path: int(
            path.stem.split("_")[1]
        )
    )

    if not page_files:

        print(
            "\nERROR: No page_*.txt files found."
        )

        return

    print("=" * 80)
    print("M2 - PAPER GROUPING TEST")
    print("=" * 80)

    print(
        f"\nFound {len(page_files)} pages."
    )

    # ==========================================================
    # 3. M1 - EXTRACT IDENTITY FROM EVERY PAGE
    # ==========================================================

    extractor = MetadataExtractor()

    page_metadata = []

    print("\n")
    print("=" * 80)
    print("M1 OUTPUT")
    print("=" * 80)

    for page_file in page_files:

        text = page_file.read_text(
            encoding="utf-8"
        )

        metadata = extractor.extract_page_identity(
            text
        )

        page_number = int(
            page_file.stem.split("_")[1]
        )

        page_metadata.append(
            (
                page_number,
                metadata,
            )
        )

        print(
            f"\nPage {page_number}"
        )

        print(
            json.dumps(
                metadata,
                indent=4,
                ensure_ascii=False,
            )
        )

    # ==========================================================
    # 4. M2 - GROUP PAGES
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("M2 OUTPUT - PAPERS")
    print("=" * 80)

    papers = PaperGrouper.group(
        page_metadata
    )

    # ==========================================================
    # 5. DISPLAY PAPERS
    # ==========================================================

    if not papers:

        print(
            "\nNo papers detected."
        )

        return

    for index, paper in enumerate(
        papers,
        start=1,
    ):

        print("\n" + "-" * 80)

        print(
            f"PAPER {index}"
        )

        print(
            f"Paper ID     : {paper.paper_id}"
        )
        
        print(
            f"Subject      : {paper.subject}"
        )

        print(
            f"Subject Code : {paper.subject_code}"
        )

        print(
            f"Exam Type    : {paper.exam_type}"
        )

        print(
            f"Semester     : {paper.semester}"
        )

        print(
            f"Pages        : {paper.pages}"
        )

    
        # ==========================================================
    # 6. SAVE PAPER GROUPING
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("SAVING PAPER GROUPING")
    print("=" * 80)

    storage = PaperStorage()

    output_file = storage.save(
        document_name="6thsempyqs_2025",
        papers=papers,
    )

    print(
        f"\n✓ Papers saved to:\n"
        f"{output_file}"
    )

    # ==========================================================
    # 7. LOAD IT BACK AND VERIFY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("VERIFYING SAVED FILE")
    print("=" * 80)

    saved_data = storage.load(
        "6thsempyqs_2025"
    )

    print(
        json.dumps(
            saved_data,
            indent=4,
            ensure_ascii=False,
        )
    )

    print("\n✓ Save + Load verification successful.")
    
    print("\n" + "=" * 80)
    print("M2 TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()