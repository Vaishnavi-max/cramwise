
from app.parsers.syllabus_parser import SyllabusParser

parser = SyllabusParser()

pdf_path = "uploads/syllabus/B.tech - CSE CBCS  Syllabus (1)-1.PDF"

courses = parser.parse(pdf_path)

print(f"Total courses: {len(courses)}\n")

for course in courses:

    print("=" * 80)

    for course in courses:

        print({
            "course_name": course["course_name"],
            "course_code": course["course_code"],
            "category": course["category"],
            "credits": course["credits"],
            "semester": course["semester"]
        })

        print()

        print("Units")
        for unit in course["units"]:
            print(unit)

        print()

        print("Text Books")
        for book in course["text_books"]:
            print(book)

        print()

        print("Reference Books")
        for book in course["reference_books"]:
            print(book)

        print()