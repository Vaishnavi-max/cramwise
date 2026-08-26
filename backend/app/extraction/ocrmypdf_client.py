import subprocess
from pathlib import Path


class OCRmyPDFClient:
    """
    Wrapper around the local OCRmyPDF command.

    Converts a scanned/image-based PDF into a searchable PDF
    by adding an OCR text layer using Tesseract.
    """

    def process_pdf(
        self,
        input_pdf: Path,
        output_pdf: Path,
    ) -> Path:

        input_pdf = Path(input_pdf)
        output_pdf = Path(output_pdf)

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------

        if not input_pdf.exists():
            raise FileNotFoundError(
                f"Input PDF not found: {input_pdf}"
            )

        # --------------------------------------------------
        # If OCR PDF already exists, reuse it
        # --------------------------------------------------

        if output_pdf.exists():
            print(
                f"✓ OCR PDF already exists:\n"
                f"  {output_pdf}"
            )

            return output_pdf

        # --------------------------------------------------
        # Create output directory
        # --------------------------------------------------

        output_pdf.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Run OCRmyPDF
        # --------------------------------------------------

        command = [
            "ocrmypdf",

            "--force-ocr",

            "--deskew",

            "--rotate-pages",

            "-l",
            "eng",

            str(input_pdf),

            str(output_pdf),
        ]

        print("\n" + "=" * 80)
        print("RUNNING OCRMY PDF")
        print("=" * 80)

        print(
            "\nInput : "
            f"{input_pdf}"
        )

        print(
            "Output: "
            f"{output_pdf}"
        )

        try:

            subprocess.run(
                command,
                check=True,
            )

        except FileNotFoundError as exc:

            raise RuntimeError(
                "ocrmypdf command was not found. "
                "Make sure OCRmyPDF is installed "
                "and available in PATH."
            ) from exc

        except subprocess.CalledProcessError as exc:

            raise RuntimeError(
                "OCRmyPDF failed while processing "
                f"{input_pdf}"
            ) from exc

        # --------------------------------------------------
        # Verify output
        # --------------------------------------------------

        if not output_pdf.exists():

            raise RuntimeError(
                "OCRmyPDF completed but the output "
                "PDF was not created."
            )

        print(
            "\n✓ OCR completed successfully."
        )

        print(
            f"✓ OCR PDF: {output_pdf}"
        )

        return output_pdf