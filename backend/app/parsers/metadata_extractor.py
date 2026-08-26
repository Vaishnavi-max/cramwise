from pathlib import Path
import json
import logging
import re

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Extracts examination-paper metadata.

    Supports two use cases:

    1. extract()
       Extract complete metadata from a paper/header page.

    2. extract_page_identity()
       Check one page to see whether it contains the
       beginning/header of a new examination paper.
    """

    def __init__(
        self,
        metadata_dir: Path | None = None,
    ):
        self.metadata_dir = metadata_dir

    # ==========================================================
    # EXISTING FULL METADATA EXTRACTION
    # ==========================================================

    def extract(self, text: str) -> dict:
        """
        Extract complete metadata from examination text.

        This is useful when the text is known to contain
        the paper header.
        """

        metadata = {
            "exam_type": None,
            "subject": None,
            "subject_code": None,
            "semester": None,
            "duration": None,
            "maximum_marks": None,
        }

        if not text:
            return metadata

        # ------------------------------------------------------
        # Exam Type
        # ------------------------------------------------------

        exam = re.search(
            r"\b(MID[\s-]*TERM|END[\s-]*TERM)"
            r"(?:[\s-]+EXAMINATION)?\b",
            text,
            re.IGNORECASE,
        )

        if exam:
            exam_type = exam.group(1).upper()

            # Normalize spelling
            if "MID" in exam_type:
                metadata["exam_type"] = "MIDTERM"
            elif "END" in exam_type:
                metadata["exam_type"] = "ENDTERM"

        # ------------------------------------------------------
        # Subject
        # ------------------------------------------------------

        subject = re.search(
            r"^\s*Subject\s*:\s*(.+?)\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if subject:
            metadata["subject"] = subject.group(1).strip()

        # ------------------------------------------------------
        # Subject Code
        # ------------------------------------------------------

        subject_code = re.search(
            r"^\s*Subject\s*Code\s*:\s*(.+?)\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if subject_code:
            metadata["subject_code"] = (
                subject_code.group(1).strip()
            )

        # ------------------------------------------------------
        # Semester
        # Handles:
        #
        # Semester: 6
        # Semester: 6th
        # Semester : 6
        # ------------------------------------------------------

        semester = re.search(
            r"\bSemester\s*:\s*(\d+)",
            text,
            re.IGNORECASE,
        )

        if semester:
            metadata["semester"] = int(
                semester.group(1)
            )

        # ------------------------------------------------------
        # Duration
        # ------------------------------------------------------

        duration = re.search(
            r"^\s*Time\s*:\s*(.+?)\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if duration:
            metadata["duration"] = (
                duration.group(1).strip()
            )

        # ------------------------------------------------------
        # Maximum Marks
        # ------------------------------------------------------

        marks = re.search(
            r"^\s*Maximum\s*Marks\s*:\s*(\d+)",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if marks:
            metadata["maximum_marks"] = int(
                marks.group(1)
            )

        return metadata

    # ==========================================================
    # PAGE-LEVEL PAPER IDENTITY
    # ==========================================================

    def extract_page_identity(self, text: str) -> dict:
        """
        Examine ONE cleaned OCR page.

        Determines whether the page explicitly contains
        an examination-paper header.

        Returns only identity information:

            exam_type
            subject
            subject_code
            semester

        If the page is a continuation page, the fields
        will normally be None.

        This method DOES NOT decide which previous paper
        an unlabeled page belongs to.

        That will be handled by PaperGrouper in M2.
        """

        identity = {
            "exam_type": None,
            "subject": None,
            "subject_code": None,
            "semester": None,
        }

        if not text:
            return identity

        # ------------------------------------------------------
        # Exam Type
        # ------------------------------------------------------

        exam = re.search(
            r"\b(MID[\s-]*TERM|END[\s-]*TERM)"
            r"(?:[\s-]+EXAMINATION)?\b",
            text,
            re.IGNORECASE,
        )

        if exam:

            exam_type = exam.group(1).upper()

            if "MID" in exam_type:
                identity["exam_type"] = "MIDTERM"

            elif "END" in exam_type:
                identity["exam_type"] = "ENDTERM"

        # ------------------------------------------------------
        # Subject
        # ------------------------------------------------------

        subject = re.search(
            r"^\s*Subject\s*:\s*(.+?)\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if subject:

            value = subject.group(1).strip()

            if value:
                identity["subject"] = value

        # ------------------------------------------------------
        # Subject Code
        # ------------------------------------------------------

        subject_code = re.search(
            r"^\s*Subject\s*Code\s*:\s*(.+?)\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if subject_code:

            value = subject_code.group(1).strip()

            if value:
                identity["subject_code"] = value

        # ------------------------------------------------------
        # Semester
        # ------------------------------------------------------

        semester = re.search(
            r"\bSemester\s*:\s*(\d+)",
            text,
            re.IGNORECASE,
        )

        if semester:

            identity["semester"] = int(
                semester.group(1)
            )

        return identity

    # ==========================================================
    # CACHE EXISTING DOCUMENT METADATA
    # ==========================================================

    def get_metadata(
        self,
        first_page_text: str,
        document_name: str,
    ) -> dict:
        """
        Returns document metadata.

        Existing behavior:

        metadata.json exists
            ↓
        load it

        otherwise
            ↓
        extract metadata from first page
            ↓
        save metadata.json
        """

        metadata_dir = (
            Path("uploads/temp/metadata")
            / document_name
        )

        metadata_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        metadata_file = (
            metadata_dir
            / "metadata.json"
        )

        # ------------------------------------------------------
        # Cached metadata
        # ------------------------------------------------------

        if metadata_file.exists():

            logger.info(
                "Loading metadata from %s",
                metadata_file.name,
            )

            return json.loads(
                metadata_file.read_text(
                    encoding="utf-8",
                )
            )

        # ------------------------------------------------------
        # Extract
        # ------------------------------------------------------

        logger.info(
            "Extracting document metadata..."
        )

        metadata = self.extract(
            first_page_text
        )

        metadata_file.write_text(
            json.dumps(
                metadata,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        logger.info(
            "Saved metadata to %s",
            metadata_file.name,
        )

        return metadata