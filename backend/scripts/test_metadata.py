from pathlib import Path
import json

from app.parsers.metadata_extractor import MetadataExtractor


def main():

    cleaned_dir = Path(
        "uploads/temp/cleaned/6thsempyqs_2025"
    )

    if not cleaned_dir.exists():

        print(
            f"\nERROR: Folder not found:\n"
            f"{cleaned_dir.resolve()}"
        )

        return

    # ------------------------------------------------------
    # Find pages
    # ------------------------------------------------------

    page_files = sorted(
        cleaned_dir.glob("page_*.txt"),
        key=lambda path: int(
            path.stem.split("_")[1]
        ),
    )

    if not page_files:

        print(
            "\nERROR: No page_*.txt files found."
        )

        return

    extractor = MetadataExtractor()

    print("=" * 80)
    print("TESTING PAGE-LEVEL PAPER IDENTITY EXTRACTION")
    print("=" * 80)

    print(
        f"\nFolder:\n{cleaned_dir.resolve()}"
    )

    print(
        f"\nFound {len(page_files)} pages.\n"
    )

    # ------------------------------------------------------
    # Test every page
    # ------------------------------------------------------

    for page_file in page_files:

        print("\n" + "-" * 80)
        print(page_file.name)
        print("-" * 80)

        text = page_file.read_text(
            encoding="utf-8"
        )

        identity = extractor.extract_page_identity(
            text
        )

        print(
            json.dumps(
                identity,
                indent=4,
                ensure_ascii=False,
            )
        )

        # --------------------------------------------------
        # Helpful classification
        # --------------------------------------------------

        has_identity = any(
            value is not None
            for value in identity.values()
        )

        if has_identity:

            print(
                "\n>>> PAPER HEADER DETECTED"
            )

        else:

            print(
                "\n>>> NO PAPER HEADER DETECTED"
            )

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()