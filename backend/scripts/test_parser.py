from app.parsers.syllabus_parser import SyllabusParser

parser = SyllabusParser()

pdf_path = "uploads/syllabus/B.tech - CSE CBCS  Syllabus (1)-1.PDF"

lines = parser.extract_text(pdf_path)

print(f"Total lines: {len(lines)}\n")

course_blocks = parser.split_into_courses(lines)

print(f"Total courses: {len(course_blocks)}\n")

for block in course_blocks:

    info = parser.extract_course_info(block)
    units = parser.extract_units(block)
    text_books = parser.extract_text_books(block)
    reference_books = parser.extract_reference_books(block)

    print("=" * 80)
    print(info)
    print()

    print("Units")
    for unit in units:
        print(unit)

    print()

    print("Text Books")
    for book in text_books:
        print(book)

    print()

    print("Reference Books")
    for book in reference_books:
        print(book)

    print()