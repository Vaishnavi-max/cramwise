from collections import defaultdict


class SyllabusCatalogService:
    """
    M2 — Syllabus Catalog Service.

    Responsible for organizing the syllabus index so that
    M4 can quickly retrieve the relevant syllabus records
    for a question.

    Important:
    Course codes may appear in slightly different formats
    between PYQs and syllabus.

        HMC-306
        HMC 306
        HMC306

    should all be treated as the same course internally.
    """

    def __init__(self, syllabus_records: list[dict]):
        """
        Store the syllabus records and build lookup indexes.
        """

        self.records = syllabus_records

        # --------------------------------------------------
        # MAIN LOOKUP
        # --------------------------------------------------

        # Key:
        #
        #     (normalized_course_code, unit_number)
        #
        # Value:
        #
        #     list of syllabus records
        #
        self.unit_index = {}

        # --------------------------------------------------
        # SUBJECT LOOKUP
        # --------------------------------------------------

        self.subject_index = {}

        # Build the indexes.
        self._build_indexes()

    # ======================================================
    # COURSE CODE NORMALIZATION
    # ======================================================

    @staticmethod
    def normalize_course_code(course_code: str) -> str:
        """
        Convert different representations of the same course
        code into one canonical comparison format.

        Examples:

            HMC-306 -> HMC306
            HMC 306 -> HMC306
            HMC306  -> HMC306
            BCS 302 -> BCS302
            BCS-302 -> BCS302

        We use this ONLY for comparison.

        The original course_code stored in the syllabus
        record is never modified.
        """

        if not course_code:
            return ""

        return (
            str(course_code)
            .upper()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

    # ======================================================
    # BUILD INDEXES
    # ======================================================

    def _build_indexes(self):
        """
        Build fast lookup dictionaries from the syllabus
        records.
        """

        for record in self.records:

            course_code = self.normalize_course_code(
                record.get("course_code", "")
            )

            unit_number = record.get("unit_number")

            # --------------------------------------------------
            # SUBJECT INDEX
            # --------------------------------------------------

            self.subject_index.setdefault(
                course_code,
                []
            ).append(record)

            # --------------------------------------------------
            # UNIT INDEX
            # --------------------------------------------------

            key = (
                course_code,
                unit_number
            )

            self.unit_index.setdefault(
                key,
                []
            ).append(record)

    # ======================================================
    # GET ALL SUBJECT RECORDS
    # ======================================================

    def get_subject_catalog(
        self,
        course_code: str,
    ) -> list[dict]:
        """
        Return all syllabus records belonging to a subject.

        Course-code formatting differences are ignored.
        """

        normalized_code = (
            self.normalize_course_code(
                course_code
            )
        )

        return self.subject_index.get(
            normalized_code,
            []
        )

    # ======================================================
    # GET UNIT RECORDS
    # ======================================================

    def get_unit_catalog(
        self,
        course_code: str,
        unit_number: int,
    ) -> list[dict]:
        """
        Return syllabus records for one subject + one unit.

        Example:

            get_unit_catalog("HMC-306", 1)

        will correctly find records stored as:

            HMC 306
        """

        normalized_code = (
            self.normalize_course_code(
                course_code
            )
        )

        key = (
            normalized_code,
            unit_number
        )

        return self.unit_index.get(
            key,
            []
        )

    # ======================================================
    # GET RECORD BY ID
    # ======================================================

    def get_by_id(
        self,
        index_id: str,
    ) -> dict | None:
        """
        Return one syllabus record using its index_id.
        """

        for record in self.records:

            if record.get("index_id") == index_id:
                return record

        return None

    # ======================================================
    # GET TOPIC IDS
    # ======================================================

    def get_topic_ids(
        self,
        course_code: str,
        unit_number: int,
    ) -> list[str]:
        """
        Return all syllabus index_ids belonging to a
        particular subject and unit.
        """

        records = self.get_unit_catalog(
            course_code,
            unit_number
        )

        return [
            record["index_id"]
            for record in records
        ]

    # ======================================================
    # COUNT
    # ======================================================

    def count(self) -> int:
        """
        Return total number of syllabus records.
        """

        return len(self.records)