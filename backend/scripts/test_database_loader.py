from app.parsers.syllabus_parser import SyllabusParser
from app.services.database_loader import DatabaseLoader

pdf_path = "uploads/syllabus/B.tech - CSE CBCS  Syllabus (1)-1.PDF"
parser = SyllabusParser()
parsed_data = parser.parse(pdf_path)

loader = DatabaseLoader()

for subject in parsed_data:
    loader.save(subject)

print("Done!")