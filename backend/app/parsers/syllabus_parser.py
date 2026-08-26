from pathlib import Path
import time
import fitz

from app.parsers.parser_client import ParserClient


class SyllabusParser:
    """
    Parses an already OCR-processed syllabus PDF.

    IMPORTANT:
    This class DOES NOT run OCR.

    Pipeline:

        OCR PDF
            ↓
        PyMuPDF text extraction
            ↓
        Chunk text
            ↓
        Groq extraction
            ↓
        Merge courses + units
    """

    def __init__(self):

        self.client = ParserClient(
            model="openai/gpt-oss-120b"
        )

        # ------------------------------------------------------
        # Keep chunks comfortably below Groq's 8000 TPM limit.
        #
        # 4000 characters ≈ roughly 1000 input tokens.
        # ------------------------------------------------------

        self.chunk_size = 4000

        # Small overlap helps when a course/unit is split
        # across two chunks.
        self.chunk_overlap = 300

        # Delay between Groq requests.
        # This helps avoid exceeding TPM limits.
        self.request_delay = 2

    # ==========================================================
    # EXTRACT TEXT FROM OCR PDF
    # ==========================================================

    def extract_text(self, pdf_path: str) -> str:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"OCR syllabus PDF not found: {pdf_path}"
            )

        print("\n" + "=" * 80)
        print("EXTRACTING TEXT FROM OCR PDF")
        print("=" * 80)

        document = fitz.open(pdf_path)

        pages = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text("text")

            print(
                f"Page {page_number}: "
                f"{len(text)} characters"
            )

            if text.strip():

                pages.append(
                    f"\n--- PAGE {page_number} ---\n"
                    f"{text.strip()}"
                )

        document.close()

        full_text = "\n\n".join(pages)

        if not full_text.strip():

            raise ValueError(
                "No text could be extracted from OCR PDF."
            )

        print(
            f"\nTotal extracted characters: "
            f"{len(full_text)}"
        )

        return full_text

    # ==========================================================
    # CREATE CHUNKS
    # ==========================================================

    def create_chunks(self, text: str) -> list:

        print("\n" + "=" * 80)
        print("CREATING SYLLABUS CHUNKS")
        print("=" * 80)

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(
                start + self.chunk_size,
                text_length
            )

            # --------------------------------------------------
            # Try to end at a newline instead of cutting
            # directly through a sentence.
            # --------------------------------------------------

            if end < text_length:

                newline_position = text.rfind(
                    "\n",
                    start,
                    end
                )

                if newline_position > start:

                    end = newline_position

            chunk = text[start:end].strip()

            if chunk:

                chunks.append(chunk)

            # --------------------------------------------------
            # Move forward while keeping a small overlap.
            # --------------------------------------------------

            next_start = end - self.chunk_overlap

            if next_start <= start:
                next_start = end

            start = next_start

        print(
            f"\n✓ Created {len(chunks)} chunks."
        )

        for i, chunk in enumerate(
            chunks,
            start=1
        ):

            print(
                f"  Chunk {i}: "
                f"{len(chunk)} characters"
            )

        return chunks

    # ==========================================================
    # GROQ PROMPT
    # ==========================================================

    def get_prompt(self) -> str:

        return """
You are a deterministic university syllabus extraction engine.

You will receive ONE CHUNK from a university syllabus.

Extract ONLY the courses, units and unit content explicitly
present in this chunk.

Return:

[
    {
        "course_name": "",
        "course_code": "",
        "semester": null,
        "units": [
            {
                "unit_number": 1,
                "content": ""
            }
        ]
    }
]

IMPORTANT RULES:

1. Use ONLY information present in the input.
2. Do NOT invent courses.
3. Do NOT invent course codes.
4. Do NOT invent units.
5. Do NOT use general knowledge.
6. Preserve course names and course codes.
7. Preserve unit content as closely as possible.
8. Ignore teaching hours, credits, textbooks and references
   unless they are part of the actual unit content.
9. If only part of a course appears in this chunk, extract
   whatever information is explicitly available.
10. If a course appears without a unit, return the course with
    "units": [].
11. Return ONLY valid JSON.
12. Do not return markdown.
13. Do not explain your answer.

INPUT CHUNK:
"""

    # ==========================================================
    # PARSE ONE CHUNK
    # ==========================================================

    def parse_chunk(
        self,
        chunk: str,
        chunk_number: int,
        total_chunks: int
    ) -> list:

        print("\n" + "-" * 80)

        print(
            f"PROCESSING CHUNK "
            f"{chunk_number}/{total_chunks}"
        )

        print(
            f"Characters: {len(chunk)}"
        )

        print("-" * 80)

        result = self.client.parse(
            text=chunk,
            prompt=self.get_prompt()
        )

        if not isinstance(result, list):

            raise ValueError(
                f"Chunk {chunk_number} did not return a list."
            )

        print(
            f"✓ Chunk {chunk_number}: "
            f"{len(result)} course entries extracted."
        )

        return result

    # ==========================================================
    # MERGE COURSES
    # ==========================================================

    def merge_courses(
        self,
        all_results: list
    ) -> list:

        print("\n" + "=" * 80)
        print("MERGING CHUNK RESULTS")
        print("=" * 80)

        courses = {}

        for result in all_results:

            for course in result:

                course_code = (
                    course.get("course_code") or ""
                ).strip()

                course_name = (
                    course.get("course_name") or ""
                ).strip()

                semester = course.get(
                    "semester"
                )

                # --------------------------------------------------
                # Prefer course code as the unique identifier.
                # If code is unavailable, use course name.
                # --------------------------------------------------

                if course_code:

                    key = course_code.lower()

                else:

                    key = course_name.lower()

                if not key:
                    continue

                # --------------------------------------------------
                # First time seeing this course
                # --------------------------------------------------

                if key not in courses:

                    courses[key] = {
                        "course_name": course_name,
                        "course_code": course_code,
                        "semester": semester,
                        "units": []
                    }

                existing = courses[key]

                # --------------------------------------------------
                # Fill missing course information
                # --------------------------------------------------

                if (
                    not existing["course_name"]
                    and course_name
                ):

                    existing["course_name"] = course_name

                if (
                    not existing["course_code"]
                    and course_code
                ):

                    existing["course_code"] = course_code

                if (
                    existing["semester"] is None
                    and semester is not None
                ):

                    existing["semester"] = semester

                # --------------------------------------------------
                # Merge units
                # --------------------------------------------------

                for unit in course.get(
                    "units",
                    []
                ):

                    unit_number = unit.get(
                        "unit_number"
                    )

                    content = (
                        unit.get("content") or ""
                    ).strip()

                    if unit_number is None:
                        continue

                    # ----------------------------------------------
                    # Check whether this unit already exists
                    # ----------------------------------------------

                    existing_unit = None

                    for saved_unit in existing["units"]:

                        if (
                            saved_unit["unit_number"]
                            == unit_number
                        ):

                            existing_unit = saved_unit
                            break

                    # ----------------------------------------------
                    # New unit
                    # ----------------------------------------------

                    if existing_unit is None:

                        existing["units"].append(
                            {
                                "unit_number": unit_number,
                                "content": content
                            }
                        )

                    # ----------------------------------------------
                    # Existing unit
                    # ----------------------------------------------

                    else:

                        old_content = (
                            existing_unit["content"]
                        )

                        if (
                            content
                            and content not in old_content
                        ):

                            if old_content:

                                existing_unit["content"] = (
                                    old_content
                                    + "\n"
                                    + content
                                )

                            else:

                                existing_unit["content"] = content

        # ======================================================
        # SORT UNITS
        # ======================================================

        final_courses = list(
            courses.values()
        )

        for course in final_courses:

            course["units"].sort(
                key=lambda unit: (
                    unit["unit_number"]
                    if isinstance(
                        unit["unit_number"],
                        int
                    )
                    else 999
                )
            )

        print(
            f"\n✓ Final unique courses: "
            f"{len(final_courses)}"
        )

        return final_courses

    # ==========================================================
    # COMPLETE PARSE
    # ==========================================================

    def parse(
        self,
        pdf_path: str
    ) -> list:

        print("\n" + "=" * 80)
        print("SYLLABUS PARSING")
        print("=" * 80)

        # ------------------------------------------------------
        # IMPORTANT:
        # pdf_path MUST already be the OCR PDF.
        #
        # We DO NOT run OCR here.
        # ------------------------------------------------------

        text = self.extract_text(
            pdf_path
        )

        # ------------------------------------------------------
        # Split into manageable pieces
        # ------------------------------------------------------

        chunks = self.create_chunks(
            text
        )

        if not chunks:

            raise ValueError(
                "No usable text chunks were created."
            )

        # ------------------------------------------------------
        # Send chunks to Groq
        # ------------------------------------------------------

        all_results = []

        total_chunks = len(chunks)

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            result = self.parse_chunk(
                chunk=chunk,
                chunk_number=index,
                total_chunks=total_chunks
            )

            all_results.append(result)

            # --------------------------------------------------
            # Avoid hitting Groq TPM too aggressively.
            # --------------------------------------------------

            if index < total_chunks:

                print(
                    f"\nWaiting "
                    f"{self.request_delay} seconds "
                    f"before next Groq request..."
                )

                time.sleep(
                    self.request_delay
                )

        # ------------------------------------------------------
        # Merge everything
        # ------------------------------------------------------

        courses = self.merge_courses(
            all_results
        )

        if not courses:

            raise ValueError(
                "No courses were extracted from the syllabus."
            )

        # ------------------------------------------------------
        # Print final result
        # ------------------------------------------------------

        print(
            f"\n✓ Courses extracted: "
            f"{len(courses)}"
        )

        for course in courses:

            print(
                f"  {course.get('course_code')} - "
                f"{course.get('course_name')}"
            )

        return courses