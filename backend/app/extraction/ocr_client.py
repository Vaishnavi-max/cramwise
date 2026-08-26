from pathlib import Path
import logging

from ollama import Client

from app.extraction.ocr_prompt import OCR_PROMPT
from app.extraction.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


class OCRClient:

    def __init__(
        self,
        model: str = "maternion/LightOnOCR-2:1b",
        host: str = "http://localhost:11434",
        ocr_dir: Path | None = None,
        cleaned_dir: Path | None = None,
    ):
        self.model = model
        self.host = host

        

        self.client = Client(host=self.host)

    def generate(
        self,
        prompt: str,
        image_paths: list[Path],
    ) -> str:
        """
        Runs OCR on the supplied image(s).

        This method ALWAYS calls Ollama.
        Use get_cleaned_page() for caching.
        """

        logger.info("Sending OCR request to Ollama...")

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [str(img.resolve()) for img in image_paths],
                }
            ],
        )

        if not response.done:
            raise RuntimeError(
                f"Ollama returned an incomplete response: {response}"
            )

        logger.info("OCR completed.")

        return response.message.content

    def get_cleaned_page(
        self,
        image_path: Path,
        document_name: str,
    ) -> str:
        """
        Returns cleaned OCR text for a page.

        Priority:

        cleaned text
            ↓
        OCR text
            ↓
        Run OCR
        """

        page_name = image_path.stem

        # Create document-specific directories
        ocr_dir = Path("uploads/temp/ocr") / document_name
        cleaned_dir = Path("uploads/temp/cleaned") / document_name

        ocr_dir.mkdir(parents=True, exist_ok=True)
        cleaned_dir.mkdir(parents=True, exist_ok=True)

        ocr_file = ocr_dir / f"{page_name}.txt"
        cleaned_file = cleaned_dir / f"{page_name}.txt"
        print("=" * 60)
        print("Checking:", cleaned_file)
        print("Exists :", cleaned_file.exists())
        print("=" * 60)

        # -----------------------------------
        # Step 1 : Cleaned file already exists
        # -----------------------------------
        if cleaned_file.exists():

            logger.info(
                "Loading cleaned text from %s",
                cleaned_file.name,
            )

            return cleaned_file.read_text(
                encoding="utf-8"
            )

        # -----------------------------------
        # Step 2 : OCR file already exists
        # -----------------------------------
        if ocr_file.exists():

            logger.info(
                "Loading cached OCR from %s",
                ocr_file.name,
            )

            raw_text = ocr_file.read_text(
                encoding="utf-8"
            )

        else:

            logger.info(
                "Running OCR for %s",
                image_path.name,
            )

            raw_text = self.generate(
                prompt=OCR_PROMPT,
                image_paths=[image_path],
            )

            ocr_file.write_text(
                raw_text,
                encoding="utf-8",
            )

            logger.info(
                "Saved OCR output to %s",
                ocr_file.name,
            )

        # -----------------------------------
        # Step 3 : Clean OCR text
        # -----------------------------------
        cleaned_text = TextCleaner.clean(raw_text)

        cleaned_file.write_text(
            cleaned_text,
            encoding="utf-8",
        )

        logger.info(
            "Saved cleaned text to %s",
            cleaned_file.name,
        )

        return cleaned_text

        
