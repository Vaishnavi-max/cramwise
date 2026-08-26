from pathlib import Path
from app.extraction.pdf_to_images import PDFToImages
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
converter = PDFToImages(dpi=300)

images = converter.convert(
    Path("uploads/pyqs/6thsempyqs_2025.pdf"),
    Path("uploads/temp/images/test"),
)

print(images)