from pathlib import Path
import subprocess

from app.parsers.syllabus_parser import SyllabusParser


class SyllabusPipelineService:
    """
    Complete syllabus processing pipeline.

    Pipeline:

        Original PDF
            ↓
        OCRmyPDF
            ↓
        Searchable OCR PDF
            ↓
        SyllabusParser
            ↓
        Structured courses + units

    OCR is performed only once.
    If the OCR PDF already exists, it is reused.
    """

    def __init__(self):
        self.parser = SyllabusParser()

    # ==========================================================
    # OCR PDF PATH
    # ==========================================================

    def get_ocr_path(self, input_pdf: str) -> Path:

        input_path = Path(input_pdf)

        return (
            input_path.parent
            / f"{input_path.stem}_ocr{input_path.suffix}"
        )

    # ==========================================================
    # RUN OCR
    # ==========================================================

    def run_ocr(self, input_pdf: str) -> Path:

        input_path = Path(input_pdf)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Input syllabus PDF not found: {input_path}"
            )

        ocr_path = self.get_ocr_path(input_pdf)

        print("\n" + "=" * 80)
        print("RUNNING OCRMYDF")
        print("=" * 80)

        print(f"Input : {input_path}")
        print(f"Output: {ocr_path}")

        # ------------------------------------------------------
        # IMPORTANT:
        # If OCR PDF already exists, DON'T OCR AGAIN.
        # ------------------------------------------------------

        if ocr_path.exists():

            print("\n✓ OCR PDF already exists.")
            print("✓ Skipping OCR.")
            print(f"✓ Using: {ocr_path}")

            return ocr_path

        # ------------------------------------------------------
        # Run OCRmyPDF
        # ------------------------------------------------------

        command = [
            "ocrmypdf",
            "--force-ocr",
            "--deskew",
            "--rotate-pages",
            "-l",
            "eng",
            str(input_path),
            str(ocr_path),
        ]

        print("\nCommand:")
        print(" ".join(command))

        try:

            subprocess.run(
                command,
                check=True,
            )

        except subprocess.CalledProcessError as e:

            raise RuntimeError(
                f"OCRmyPDF failed with exit code {e.returncode}"
            ) from e

        # ------------------------------------------------------
        # Verify output
        # ------------------------------------------------------

        if not ocr_path.exists():

            raise RuntimeError(
                "OCRmyPDF completed but the OCR PDF was not created."
            )

        print("\n✓ OCR completed successfully.")
        print(f"✓ OCR PDF: {ocr_path}")

        return ocr_path

    # ==========================================================
    # COMPLETE PIPELINE
    # ==========================================================

    def process(self, input_pdf: str) -> list:

        print("\n" + "=" * 80)
        print("SYLLABUS PIPELINE")
        print("=" * 80)

        input_path = Path(input_pdf)

        print(f"\nInput PDF:")
        print(input_path)

        # ------------------------------------------------------
        # STEP 1 — OCR
        # ------------------------------------------------------

        print("\n[1/2] Running OCR...")

        ocr_pdf = self.run_ocr(
            str(input_path)
        )

        # ------------------------------------------------------
        # STEP 2 — Parse OCR PDF
        # ------------------------------------------------------

        print("\n[2/2] Parsing OCR PDF...")

        courses = self.parser.parse(
            str(ocr_pdf)
        )

        # ------------------------------------------------------
        # RESULT
        # ------------------------------------------------------

        print("\n" + "=" * 80)
        print("SYLLABUS PIPELINE COMPLETED")
        print("=" * 80)

        print(
            f"\n✓ Courses extracted: {len(courses)}"
        )

        return courses