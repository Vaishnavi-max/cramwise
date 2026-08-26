from pathlib import Path


class PaperTextBuilder:
    """
    Builds one combined OCR text for an examination paper
    using the page numbers stored in papers.json.
    """

    def __init__(
        self,
        cleaned_base_dir: Path | None = None,
    ):
        self.cleaned_base_dir = (
            cleaned_base_dir
            if cleaned_base_dir is not None
            else Path("uploads/temp/cleaned")
        )

    def build(
        self,
        document_name: str,
        pages: list[int],
    ) -> str:
        """
        Combine cleaned OCR text from all pages
        belonging to one paper.

        Example:

        pages = [3, 4]

        returns:

        PAGE 3
        <OCR text>

        PAGE 4
        <OCR text>
        """

        document_dir = (
            self.cleaned_base_dir
            / document_name
        )

        if not document_dir.exists():
            raise FileNotFoundError(
                f"Cleaned OCR directory not found: "
                f"{document_dir}"
            )

        combined_parts = []

        for page_number in pages:

            page_file = (
                document_dir
                / f"page_{page_number}.txt"
            )

            if not page_file.exists():

                raise FileNotFoundError(
                    f"OCR file not found: "
                    f"{page_file}"
                )

            text = page_file.read_text(
                encoding="utf-8"
            )

            combined_parts.append(
                f"\n===== PAGE {page_number} =====\n\n"
                f"{text.strip()}\n"
            )

        return "\n".join(
            combined_parts
        )