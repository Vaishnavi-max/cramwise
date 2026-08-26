import sys
from pathlib import Path

from app.extraction.ocrmypdf_client import OCRmyPDFClient


def main():

    # --------------------------------------------------
    # Get input PDF from command line
    # --------------------------------------------------

    if len(sys.argv) < 2:
        print(
            "\nUsage:"
            "\npython -m scripts.test_ocrmypdf <input_pdf>"
        )
        return

    input_pdf = Path(sys.argv[1])

    # --------------------------------------------------
    # Automatically create output path
    # --------------------------------------------------

    output_dir = Path(
        "uploads/temp/ocr_pdfs"
    )

    output_pdf = (
        output_dir
        / f"{input_pdf.stem}_ocr.pdf"
    )

    # --------------------------------------------------
    # Run OCR
    # --------------------------------------------------

    client = OCRmyPDFClient()

    result = client.process_pdf(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
    )

    print("\nRESULT")
    print("-" * 80)
    print(f"Input : {input_pdf.resolve()}")
    print(f"Output: {result.resolve()}")


if __name__ == "__main__":
    main()