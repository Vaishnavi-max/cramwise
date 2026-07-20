from app.parsers.syllabus_parser import SyllabusParser

parser = SyllabusParser()

text = parser.extract_text(
    "uploads/syllabus/B.tech - CSE CBCS  Syllabus (1)-1.PDF"
)

print(text)