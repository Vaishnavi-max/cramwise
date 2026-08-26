from pathlib import Path
import logging

from app.extraction.pdf_to_images import PDFToImages
from app.extraction.ocr_client import OCRClient
from app.extraction.ocr_prompt import OCR_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# -----------------------------
# Input PDF
# -----------------------------
pdf = Path("uploads/pyqs/6thsempyqs_2025.pdf")

# Folder to store page images
image_output = Path("uploads/temp/images/test")

# Convert PDF -> Images
converter = PDFToImages(dpi=200)
images = converter.convert(pdf, image_output)

# OCR Client
client = OCRClient()

# Folder to store OCR output
ocr_output = Path("uploads/temp/ocr")
ocr_output.mkdir(parents=True, exist_ok=True)

# -----------------------------------
# OCR every page
# -----------------------------------
for image in images:
    print(f"\nProcessing {image.name}...")

    try:

        text = client.generate(
            prompt=OCR_PROMPT,
            image_paths=[image],
        )

        output_file = ocr_output / f"{image.stem}.txt"

        output_file.write_text(
            text,
            encoding="utf-8",
        )

        print(f"✓ Saved: {output_file.name}")

    except Exception as e:

        print(f"✗ Failed: {image.name}")
        print(e)

print("\nFinished processing all pages.")