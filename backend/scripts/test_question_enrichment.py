import json
from pathlib import Path

from app.services.question_enrichment_service import (
    QuestionEnrichmentService,
)
def main():

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    document_name = "6thsempyqs_2025"

    # ==========================================================
    # FILE LOCATIONS
    # ==========================================================

    papers_file = (
        Path("uploads/temp/papers")
        / document_name
        / "papers.json"
    )

    parsed_dir = (
        Path("uploads/temp/parsed")
        / document_name
    )

    enriched_dir = (
        Path("uploads/temp/enriched")
        / document_name
    )

    # ==========================================================
    # CHECK PAPERS.JSON
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

    papers_data = json.loads(
        papers_file.read_text(
            encoding="utf-8"
        )
    )

    papers = papers_data.get(
        "papers",
        []
    )

    print("=" * 80)
    print("M4.3 - ALL PAPER QUESTION ENRICHMENT")
    print("=" * 80)

    print(
        f"\nFound {len(papers)} papers."
    )

    # ==========================================================
    # CREATE SERVICE
    # ==========================================================

    service = QuestionEnrichmentService()

    successful = 0
    failed = 0

    # ==========================================================
    # PROCESS EVERY PAPER
    # ==========================================================

    for paper in papers:

        paper_id = paper.get(
            "paper_id"
        )

        print("\n" + "-" * 80)

        print(
            f"Paper: {paper_id}"
        )

        # ------------------------------------------
        # Parsed question file
        # ------------------------------------------

        parsed_file = (
            parsed_dir
            / f"{paper_id}_questions.json"
        )

        # ------------------------------------------
        # Enriched output file
        # ------------------------------------------

        output_file = (
            enriched_dir
            / f"{paper_id}_questions.json"
        )

        # ------------------------------------------
        # Check parsed file
        # ------------------------------------------

        if not parsed_file.exists():

            print(
                f"❌ Parsed file not found:"
                f" {parsed_file.name}"
            )

            failed += 1
            continue

        # ------------------------------------------
        # Enrich
        # ------------------------------------------

        try:

            enriched_questions = (
                service.enrich_paper(
                    question_file=parsed_file,
                    paper_metadata=paper,
                    output_file=output_file,
                )
            )

            print(
                f"✓ {paper_id} "
                f"→ {len(enriched_questions)} questions"
            )

            print(
                f"  Saved: {output_file.name}"
            )

            successful += 1

        except Exception as e:

            print(
                f"❌ {paper_id} → FAILED"
            )

            print(
                f"   {type(e).__name__}: {e}"
            )

            failed += 1

    # ==========================================================
    # FINAL SUMMARY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("M4.3 SUMMARY")
    print("=" * 80)

    print(
        f"\nSuccessful : {successful}"
    )

    print(
        f"Failed     : {failed}"
    )

    print(
        f"Total      : {len(papers)}"
    )

    print(
        f"\nOutput directory:"
    )

    print(
        enriched_dir.resolve()
    )

    print("\n" + "=" * 80)
if __name__ == "__main__":
    main()