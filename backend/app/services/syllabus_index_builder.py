from pathlib import Path
import json
import re


class SyllabusIndexBuilder:
    """
    Converts hierarchical syllabus_structure.json into
    a flat syllabus_index.json suitable for embeddings
    and semantic retrieval.

    Source:
        Course
            -> Unit
                -> Topic
                    -> Subtopics

    Output:
        One flat record per subtopic.

    If a topic has no subtopics, the topic itself becomes
    one index record with subtopic=None.
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        input_file: Path,
        output_file: Path,
    ):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)

    # ==========================================================
    # LOAD SYLLABUS
    # ==========================================================

    def load_syllabus(self) -> list:
        """
        Load syllabus_structure.json.
        """

        if not self.input_file.exists():
            raise FileNotFoundError(
                f"Syllabus file not found: {self.input_file}"
            )

        with self.input_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "syllabus_structure.json must contain a list of courses."
            )

        return data

    # ==========================================================
    # NORMALIZE COURSE CODE
    # ==========================================================

    @staticmethod
    def normalize_course_code(course_code: str) -> str:
        """
        Convert:

            BCS 306
            ->
            BCS306

        Used only for generating index IDs.
        """

        return re.sub(
            r"[^A-Za-z0-9]",
            "",
            str(course_code),
        ).upper()

    # ==========================================================
    # BUILD INDEX ID
    # ==========================================================

    @staticmethod
    def build_index_id(
        course_code: str,
        unit_number: int,
        topic_number: int,
        subtopic_number: int | None = None,
    ) -> str:
        """
        Examples:

        BCS306_U2_T01_S01
        BCS306_U2_T01_S02
        BCS306_U2_T02

        Topic without subtopics does not receive Sxx.
        """

        course_code = SyllabusIndexBuilder.normalize_course_code(
            course_code
        )

        index_id = (
            f"{course_code}"
            f"_U{unit_number}"
            f"_T{topic_number:02d}"
        )

        if subtopic_number is not None:
            index_id += f"_S{subtopic_number:02d}"

        return index_id

    # ==========================================================
    # BUILD SEARCH TEXT
    # ==========================================================

    @staticmethod
    def build_search_text(
        course_name: str,
        unit_number: int,
        topic: str,
        subtopic: str | None,
    ) -> str:
        """
        Creates the text that will later be embedded.

        Example:

        Compiler Design | Unit 2 | Top-Down Parsing |
        Recursive Descent parsing
        """

        parts = [
            course_name,
            f"Unit {unit_number}",
            topic,
        ]

        if subtopic:
            parts.append(subtopic)

        return " | ".join(
            str(part).strip()
            for part in parts
            if str(part).strip()
        )

    # ==========================================================
    # BUILD INDEX
    # ==========================================================

    def build(self) -> list:
        """
        Flatten the complete syllabus hierarchy.
        """

        syllabus = self.load_syllabus()

        index = []

        for course in syllabus:

            course_name = course.get(
                "course_name",
                "",
            )

            course_code = course.get(
                "course_code",
                "",
            )

            semester = course.get(
                "semester",
            )

            units = course.get(
                "units",
                [],
            )

            for unit in units:

                unit_number = unit.get(
                    "unit_number"
                )

                topics = unit.get(
                    "topics",
                    [],
                )

                for topic_number, topic_data in enumerate(
                    topics,
                    start=1,
                ):

                    topic = topic_data.get(
                        "topic",
                        "",
                    ).strip()

                    subtopics = topic_data.get(
                        "subtopics",
                        [],
                    )

                    # ==================================================
                    # CASE 1:
                    # Topic has subtopics
                    # ==================================================

                    if subtopics:

                        for subtopic_number, subtopic in enumerate(
                            subtopics,
                            start=1,
                        ):

                            subtopic = str(
                                subtopic
                            ).strip()

                            if not subtopic:
                                continue

                            record = {
                                "index_id": self.build_index_id(
                                    course_code=course_code,
                                    unit_number=unit_number,
                                    topic_number=topic_number,
                                    subtopic_number=subtopic_number,
                                ),

                                "course_code": course_code,

                                "course_name": course_name,

                                "semester": semester,

                                "unit_number": unit_number,

                                "topic": topic,

                                "subtopic": subtopic,

                                "search_text": self.build_search_text(
                                    course_name=course_name,
                                    unit_number=unit_number,
                                    topic=topic,
                                    subtopic=subtopic,
                                ),
                            }

                            index.append(record)

                    # ==================================================
                    # CASE 2:
                    # Topic has NO subtopics
                    # ==================================================

                    else:

                        record = {
                            "index_id": self.build_index_id(
                                course_code=course_code,
                                unit_number=unit_number,
                                topic_number=topic_number,
                            ),

                            "course_code": course_code,

                            "course_name": course_name,

                            "semester": semester,

                            "unit_number": unit_number,

                            "topic": topic,

                            "subtopic": None,

                            "search_text": self.build_search_text(
                                course_name=course_name,
                                unit_number=unit_number,
                                topic=topic,
                                subtopic=None,
                            ),
                        }

                        index.append(record)

        return index

    # ==========================================================
    # SAVE INDEX
    # ==========================================================

    def save(
        self,
        index: list,
    ) -> None:
        """
        Save the generated syllabus index.
        """

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                index,
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # RUN
    # ==========================================================

    def run(self) -> list:
        """
        Complete build pipeline.
        """

        print("=" * 80)
        print("M6.1 - SYLLABUS INDEX BUILDER")
        print("=" * 80)

        print(
            f"\nInput : {self.input_file}"
        )

        print(
            f"Output: {self.output_file}"
        )

        print("\nLoading syllabus...")

        index = self.build()

        print(
            f"✓ Created {len(index)} index records."
        )

        self.save(index)

        print(
            f"✓ Saved syllabus index to:"
            f"\n  {self.output_file}"
        )

        print("\n" + "=" * 80)
        print("M6.1 COMPLETED")
        print("=" * 80)

        return index