import json
from pathlib import Path

from app.parsers.parser_client import ParserClient
from app.parsers.syllabus_topic_prompt import (
    SYLLABUS_TOPIC_PROMPT,
)


class SyllabusTopicService:

    def __init__(self):
        self.client = ParserClient(
            model="openai/gpt-oss-120b"
        )

    def structure_unit(
        self,
        unit_number: int,
        content: str,
    ) -> dict:

        prompt = (
            SYLLABUS_TOPIC_PROMPT
            + f"\n\nUNIT NUMBER: {unit_number}\n\n"
            + content
        )

        return self.client.parse(
            text="",
            prompt=prompt,
        )

    def structure_all(
        self,
        syllabus_data: list,
        output_file: Path,
    ) -> list:

        # ---------------------------------------------
        # Load existing output if available
        # ---------------------------------------------

        if output_file.exists():

            structured_courses = json.loads(
                output_file.read_text(
                    encoding="utf-8"
                )
            )

        else:

            structured_courses = []

        # ---------------------------------------------
        # Process every course
        # ---------------------------------------------

        for course in syllabus_data:

            course_code = course.get(
                "course_code"
            )

            print("\n" + "=" * 80)
            print(
                f"COURSE: {course_code} - "
                f"{course.get('course_name')}"
            )
            print("=" * 80)

            # Find existing course
            existing_course = next(
                (
                    c for c in structured_courses
                    if c.get("course_code")
                    == course_code
                ),
                None,
            )

            if existing_course is None:

                existing_course = {
                    "course_name": course.get(
                        "course_name"
                    ),
                    "course_code": course_code,
                    "semester": course.get(
                        "semester"
                    ),
                    "units": [],
                }

                structured_courses.append(
                    existing_course
                )

            # -----------------------------------------
            # Every unit
            # -----------------------------------------

            for unit in course.get(
                "units",
                []
            ):

                unit_number = unit.get(
                    "unit_number"
                )

                # Already processed?
                existing_unit = next(
                    (
                        u
                        for u in existing_course["units"]
                        if u.get("unit_number")
                        == unit_number
                    ),
                    None,
                )

                if existing_unit is not None:

                    print(
                        f"✓ Unit {unit_number} "
                        f"already exists"
                    )

                    continue

                print(
                    f"\n→ Structuring Unit "
                    f"{unit_number}..."
                )

                try:

                    structured_unit = (
                        self.structure_unit(
                            unit_number=unit_number,
                            content=unit.get(
                                "content",
                                ""
                            ),
                        )
                    )

                    existing_course[
                        "units"
                    ].append(
                        structured_unit
                    )

                    # Save immediately
                    output_file.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    output_file.write_text(
                        json.dumps(
                            structured_courses,
                            indent=4,
                            ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )

                    print(
                        f"✓ Unit {unit_number} "
                        f"completed"
                    )

                except Exception as e:

                    print(
                        f"✗ Unit {unit_number} "
                        f"FAILED"
                    )

                    print(
                        f"  Error: {e}"
                    )

        return structured_courses