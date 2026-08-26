from pathlib import Path

from app.services.syllabus_index_builder import (
    SyllabusIndexBuilder,
)


def main():

    input_file = Path(
        "uploads/temp/syllabus/syllabus_structure.json"
    )

    output_file = Path(
        "uploads/temp/syllabus/syllabus_index.json"
    )

    builder = SyllabusIndexBuilder(
        input_file=input_file,
        output_file=output_file,
    )

    index = builder.run()

    print("\nSTATISTICS")
    print("-" * 80)

    print(
        f"Total index records : {len(index)}"
    )

    courses = {
        record["course_code"]
        for record in index
    }

    print(
        f"Courses             : {len(courses)}"
    )

    topics = {
        (
            record["course_code"],
            record["unit_number"],
            record["topic"],
        )
        for record in index
    }

    print(
        f"Unique topics       : {len(topics)}"
    )

    records_with_subtopics = sum(
        1
        for record in index
        if record["subtopic"] is not None
    )

    records_without_subtopics = sum(
        1
        for record in index
        if record["subtopic"] is None
    )

    print(
        f"Subtopic records    : "
        f"{records_with_subtopics}"
    )

    print(
        f"Topic-only records : "
        f"{records_without_subtopics}"
    )

    print("\nFIRST 5 RECORDS")
    print("-" * 80)

    for record in index[:5]:
        print(record)

    print("\nLAST 5 RECORDS")
    print("-" * 80)

    for record in index[-5:]:
        print(record)


if __name__ == "__main__":
    main()