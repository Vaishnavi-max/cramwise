import json
from pathlib import Path

from app.extraction.ocrmypdf_client import OCRmyPDFClient
from app.parsers.syllabus_parser import SyllabusParser
from app.services.syllabus_index_builder import SyllabusIndexBuilder
from app.services.syllabus_topic_service import SyllabusTopicService
from app.validators.syllabus.syllabus_structure_validator import (
    SyllabusStructureValidator,
)


class SyllabusPipelineService:
    """
    Build every JSON artifact required after a syllabus PDF is uploaded.

    Pipeline:

        Original PDF
            ↓
        OCRmyPDF + Tesseract (cached searchable PDF)
            ↓
        SyllabusParser (raw courses and units)
            ↓
        syllabus_raw.json
            ↓
        SyllabusTopicService (topics and subtopics)
            ↓
        syllabus_structure.json
            ↓
        SyllabusStructureValidator
            ↓
        SyllabusIndexBuilder
            ↓
        syllabus_index.json

    This service deliberately produces files rather than database records:
    JSON is CramWise's approved primary storage format. Background execution
    is intentionally outside this service and will be addressed separately.
    """

    def __init__(self):
        # Keep all derived syllabus data under the existing temporary-data
        # directory so uploads/ contains originals and temp/ contains outputs.
        backend_dir = Path(__file__).resolve().parents[2]
        self.syllabus_dir = backend_dir / "uploads" / "temp" / "syllabus"
        self.ocr_dir = backend_dir / "uploads" / "temp" / "ocr_pdfs"

        self.raw_file = self.syllabus_dir / "syllabus_raw.json"
        self.structure_file = self.syllabus_dir / "syllabus_structure.json"
        self.index_file = self.syllabus_dir / "syllabus_index.json"

        # Reuse dedicated services so OCR, parsing, structuring, validation,
        # and indexing each keep their own single responsibility.
        self.ocr_client = OCRmyPDFClient()
        self.parser = SyllabusParser()
        self.topic_service = SyllabusTopicService()

    def get_ocr_path(self, input_pdf: str | Path) -> Path:
        """Return the standard cached OCR location for a syllabus PDF."""

        input_path = Path(input_pdf)
        return self.ocr_dir / f"{input_path.stem}_ocr.pdf"

    def get_reusable_ocr_path(
        self,
        input_pdf: str | Path,
    ) -> Path | None:
        """
        Locate a cached searchable PDF without invoking OCR.

        New OCR files belong in uploads/temp/ocr_pdfs. The former upload-side
        location is also checked so existing user data remains reusable while
        the pipeline adopts the shared OCRmyPDFClient output convention.
        """

        input_path = Path(input_pdf)
        standard_path = self.get_ocr_path(input_path)
        legacy_path = input_path.parent / f"{input_path.stem}_ocr{input_path.suffix}"

        for cached_path in (standard_path, legacy_path):
            if cached_path.exists():
                return cached_path

        return None

    def run_ocr(self, input_pdf: str | Path) -> Path:
        """Reuse an OCR cache when present, otherwise create one once."""

        input_path = Path(input_pdf)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Input syllabus PDF not found: {input_path}"
            )

        cached_path = self.get_reusable_ocr_path(input_path)
        if cached_path is not None:
            print(f"✓ Reusing cached OCR PDF: {cached_path}")
            return cached_path

        # OCRmyPDFClient owns the Tesseract subprocess call and its output
        # verification, avoiding a second copy of OCR command logic here.
        return self.ocr_client.process_pdf(
            input_pdf=input_path,
            output_pdf=self.get_ocr_path(input_path),
        )

    @staticmethod
    def save_json(
        data: list,
        output_file: Path,
    ) -> None:
        """Persist a completed pipeline stage as readable UTF-8 JSON."""

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    def process(self, input_pdf: str | Path) -> list:
        """
        Run the full synchronous syllabus pipeline and return raw courses.

        The return value stays a list for compatibility with the current
        upload endpoint. The durable outputs for later stages are the three
        JSON files written during this method.
        """

        input_path = Path(input_pdf)

        # 1. Create or reuse a searchable PDF before extracting its text.
        ocr_pdf = self.run_ocr(input_path)

        # 2. Extract raw course/unit information and save it before using the
        # LLM topic stage, so raw extraction is preserved even if later work
        # fails and needs to be resumed.
        courses = self.parser.parse(str(ocr_pdf))
        if not isinstance(courses, list) or not courses:
            raise ValueError("No courses were extracted from the syllabus.")

        self.save_json(courses, self.raw_file)

        # 3. Turn raw unit content into topic/subtopic hierarchies. This
        # service keeps its existing per-unit cache and immediate checkpoints.
        structured_courses = self.topic_service.structure_all(
            syllabus_data=courses,
            output_file=self.structure_file,
        )

        # 4. Stop before index creation when the hierarchy is structurally
        # invalid; downstream mapping must never consume malformed syllabus data.
        validation_result = SyllabusStructureValidator.validate(structured_courses)
        if not validation_result["valid"]:
            formatted_errors = "; ".join(validation_result["errors"])
            raise ValueError(
                "Syllabus structure validation failed: "
                f"{formatted_errors}"
            )

        # 5. Flatten the validated hierarchy into records used by later M3,
        # M6.3, and retrieval stages, then persist syllabus_index.json.
        index = SyllabusIndexBuilder(
            input_file=self.structure_file,
            output_file=self.index_file,
        ).run()

        if not index:
            raise ValueError("Syllabus index generation produced no records.")

        print(
            "✓ Syllabus pipeline completed: "
            f"{len(courses)} courses, {len(index)} index records."
        )

        return courses
