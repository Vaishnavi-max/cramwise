import re


class TextCleaner:
    """
    Cleans OCR output before sending it to the parser.
    """

    @staticmethod
    def clean(text: str) -> str:
        # Remove HTML/XML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Replace HTML entities if present
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove trailing spaces
        text = "\n".join(line.rstrip() for line in text.splitlines())

        # Remove multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Collapse multiple spaces
        text = re.sub(r"[ \t]{2,}", " ", text)

        return text.strip()