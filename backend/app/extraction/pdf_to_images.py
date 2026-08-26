import logging
from pathlib import Path
import fitz
from PIL import Image
logger = logging.getLogger(__name__)

class PDFToImages:
    """
    Converts a PDF into high-resolution PNG images.
    """

    def __init__(self, dpi: int = 150):
        self.dpi = dpi
        self.scale = dpi / 72

    def convert(self, pdf_path: Path, output_dir: Path) -> list[Path]:

        logger.info(f"Starting PDF to image conversion: {pdf_path}")

        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            raise FileNotFoundError(f"{pdf_path} does not exist.")

        output_dir.mkdir(parents=True, exist_ok=True)
        # -----------------------------------
        # Check if images already exist
        # -----------------------------------
        image_paths = sorted(output_dir.glob("page_*.jpg"),key=lambda path: int(path.stem.split("_")[1]),)

        if image_paths:
            logger.info(
                "Found %d cached images. Skipping PDF conversion.",
                len(image_paths),
            )
            return image_paths

        # No cached images found
        image_paths = []

        try:
            doc = fitz.open(pdf_path)

            matrix = fitz.Matrix(self.scale, self.scale)

            for page_number, page in enumerate(doc):

                logger.info(
                    "Converting page %d of %d",
                    page_number + 1,
                    len(doc)
                )

                pix = page.get_pixmap(matrix=matrix)

                # Convert Pixmap -> PIL Image
                img = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples,
                )

                # Resize while preserving aspect ratio
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

                # Save as JPEG
                image_path = output_dir / f"page_{page_number + 1}.jpg"

                img.save(
                    image_path,
                    "JPEG",
                    quality=90,
                    optimize=True,
                )

                image_paths.append(image_path)

            doc.close()

            logger.info(f"Successfully converted {len(image_paths)} pages.")

            return image_paths

        except Exception as e:
            logger.exception("Error while converting PDF.")
            raise RuntimeError(f"Failed to convert PDF: {e}")