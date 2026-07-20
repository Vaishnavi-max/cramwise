import fitz
from typing import List


class SyllabusParser:

    def extract_text(self, pdf_path: str) -> List[str]:
        document = fitz.open(pdf_path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        return lines