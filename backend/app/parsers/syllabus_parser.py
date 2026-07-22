import fitz
from typing import List


class SyllabusParser:

    def extract_text(self, pdf_path: str) -> List[str]:
        """
    Extracts text from the syllabus PDF and returns
    a cleaned list of non-empty lines.
    """
        document = fitz.open(pdf_path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        return lines
    def split_into_courses(self, lines):
        """
    Splits the syllabus into individual course blocks.
    """
        courses = []
        start = None

        for i, line in enumerate(lines):

            if line.startswith("Course Code"):
                
                course_start = i - 1

                # we'll write the logic here
                if start is None:
                    start = course_start
                else:
                    courses.append(lines[start : course_start])
                    start = course_start
        courses.append(lines[start:])  
        return courses
    def extract_course_info(self, course_lines):
        """
        Extracts course metadata such as course name,
        course code, semester, category and credits.
        """
        course = {}

        for i, line in enumerate(course_lines):
            if line.startswith("Course Code"):
                course["course_name"] = course_lines[i - 1]
                course["course_code"] = course_lines[i].split(":", 1)[1].strip()
                course["category"] = course_lines[i + 2].split(":", 1)[1].strip()
                course["credits"] = course_lines[i + 3].split(":", 1)[1].strip()
                course["semester"] = course_lines[i + 4].split(":", 1)[1].strip()

                break

        return course
    def extract_units(self, course_lines):
        """
        Extracts all units and their corresponding topics
        from a course block.
        """
        units = []
        current_unit = None
        current_topics = []

        for line in course_lines:

            # New Unit
            if line.startswith("UNIT"):

                if current_unit is not None:
                    units.append({
                        "unit_name": current_unit,
                        "topics": current_topics
                    })

                current_unit = line
                current_topics = []

            # Units end here
            elif line == "Text Books":

                if current_unit is not None:
                    units.append({
                        "unit_name": current_unit,
                        "topics": current_topics
                    })

                break

            else:

                # Ignore everything before first UNIT
                if current_unit is None:
                    continue

                # Skip duration lines
                if "hours" in line.lower():
                    continue

                # Start of a new topic
                if ":" in line:
                    current_topics.append(line)

                # Continuation of previous topic
                elif current_topics:
                    current_topics[-1] += " " + line

        return units
    def extract_text_books(self, course_lines):
        """
        Extracts the list of prescribed textbooks.
        """
        text_books = []

        in_text_books = False
        current_book = ""

        for line in course_lines:

            if line == "Text Books":
                in_text_books = True
                continue

            if line == "Reference Books":

                if current_book:
                    text_books.append(current_book.strip())

                break

            if not in_text_books:
                continue

            # Book numbers (1,2,3...)
            if line.isdigit():

                if current_book:
                    text_books.append(current_book.strip())

                current_book = ""

            else:
                current_book += " " + line

        return text_books
    def extract_reference_books(self, course_lines):
        """
        Extracts the list of reference books.
        """
        reference_books = []

        in_reference_books = False
        current_book = ""

        for line in course_lines:

            if line == "Reference Books":
                in_reference_books = True
                continue

            if not in_reference_books:
                continue

            if line.isdigit():

                if current_book:
                    reference_books.append(current_book.strip())

                current_book = ""

            else:
                current_book += " " + line

        if current_book:
            reference_books.append(current_book.strip())

        return reference_books
    def parse(self, pdf_path):
        """
        Parses the complete syllabus PDF and returns
        structured information for all courses.
        """
        lines = self.extract_text(pdf_path)

        course_blocks = self.split_into_courses(lines)

        courses = []

        for block in course_blocks:

            info = self.extract_course_info(block)

            info["units"] = self.extract_units(block)
            info["text_books"] = self.extract_text_books(block)
            info["reference_books"] = self.extract_reference_books(block)

            courses.append(info)

        return courses