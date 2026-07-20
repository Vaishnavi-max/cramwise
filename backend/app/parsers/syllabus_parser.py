from pathlib import Path


class SyllabusParser:
    def parse(self, pdf_path: str) -> dict:
        """
        Parse a syllabus PDF and return structured data.
        """
        pdf_file = Path(pdf_path)

        return {
            "subject": "",
            "units": []
        }