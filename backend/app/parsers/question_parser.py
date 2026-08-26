from pathlib import Path
import json
import logging

# -------------------------------------------------------------------------
# DEPENDENCY IMPORTS
# -------------------------------------------------------------------------
# ParserClient handles the direct communication with Groq LLM API.
# It wraps the Groq SDK, sends prompt + OCR text, strips markdown fencing,
# and returns parsed JSON.
from app.parsers.parser_client import ParserClient

# Prompt template containing explicit instructions for parsing exam papers.
# Defines the output schema the LLM must follow (question_number, part, text, etc.).
from app.parsers.parser_prompt import QUESTION_PARSER_PROMPT

# QuestionOutputValidator performs structural checks on the parsed question list:
# - verifies expected main question numbers are present (e.g. Q1-Q9 for ENDTERM)
# - checks Q1 subparts are complete
# - detects duplicates
# - flags empty question text
from app.validators.question_output_validator import QuestionOutputValidator

# Set up module-level logger for debugging and audit logs
logger = logging.getLogger(__name__)


class QuestionParser:
    """
    Paper-oriented parser that converts raw OCR paper text into structured JSON question lists.

    Key Responsibilities:
    1. Sends cleaned multi-page examination paper text to Groq LLM using `QUESTION_PARSER_PROMPT`.
    2. Caches parsed question JSON files locally under `uploads/temp/parsed/{doc_name}/`.
    3. Validates structural output (question numbers, subparts, duplicates) via `QuestionOutputValidator`.
    """

    def __init__(self):
        """
        Initialize the parser with Groq LLM client.
        Default model used is 'openai/gpt-oss-120b' via Groq API.
        """
        self.client = ParserClient(
            model="openai/gpt-oss-120b"
        )

    # ==========================================================
    # LLM PARSING INVOCATION
    # ==========================================================

    def parse(
        self,
        text: str,
    ):
        """
        Submits complete examination paper OCR text to the LLM parser.

        :param text: Full text content of the exam paper (pages concatenated)
        :return: Raw JSON list of parsed questions returned by LLM
        """
        return self.client.parse(
            text=text,
            prompt=QUESTION_PARSER_PROMPT,
        )

    # ==========================================================
    # PAPER-LEVEL QUESTION PARSING & CACHING
    # ==========================================================

    def get_questions(
        self,
        paper_id: str,
        paper_text: str,
        document_name: str,
        exam_type: str = "ENDTERM",
    ):
        """
        Parses and validates questions for ONE complete examination paper.

        :param paper_id: Unique slug for the paper (e.g., 'BCS_306_MIDTERM')
        :param paper_text: Concatenated OCR text across all pages of this paper
        :param document_name: Source document name (e.g., '6thsempyqs_2025')
        :param exam_type: Type of exam ('MIDTERM' or 'ENDTERM') for structure validation
        :return: List of validated question dictionaries
        """

        # ------------------------------------------------------
        # 1. SETUP CACHE DIRECTORY
        # ------------------------------------------------------
        # JSON files are cached per document set under uploads/temp/parsed/<doc_name>/
        parsed_dir = Path("uploads/temp/parsed") / document_name
        parsed_dir.mkdir(parents=True, exist_ok=True)

        # File path for this paper's cached question JSON
        json_file = parsed_dir / f"{paper_id}_questions.json"

        # ------------------------------------------------------
        # 2. LOAD FROM CACHE OR CALL LLM
        # ------------------------------------------------------
        if json_file.exists():
            logger.info("Loading cached parsed questions for paper: %s", paper_id)
            parsed_questions = json.loads(json_file.read_text(encoding="utf-8"))
        else:
            logger.info("Calling LLM to parse questions for paper: %s", paper_id)
            try:
                # Invoke LLM to extract questions from raw OCR text
                parsed_questions = self.parse(paper_text)
            except ValueError as e:
                logger.error("LLM returned invalid JSON for paper: %s", paper_id)
                raise RuntimeError(
                    f"Question parsing failed for paper {paper_id}. "
                    f"The LLM returned invalid JSON."
                ) from e

            # Save the raw parsed result to JSON disk cache immediately
            json_file.write_text(
                json.dumps(parsed_questions, indent=4, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("Successfully saved parsed questions cache to: %s", json_file)

        # ------------------------------------------------------
        # 3. VALIDATE QUESTION STRUCTURE
        # ------------------------------------------------------
        # Validate paper structure using QuestionOutputValidator
        validation_result = QuestionOutputValidator.validate(
            questions=parsed_questions,
            exam_type=exam_type,
        )

        if not validation_result["valid"]:
            logger.warning(
                "Paper %s validation errors: %s",
                paper_id,
                validation_result["errors"],
            )

        # ---------------------------------------------------------------
        # NORMALIZE FIELD NAMES
        # ---------------------------------------------------------------
        # The LLM prompt (QUESTION_PARSER_PROMPT) instructs the model to
        # output a "part" field (e.g. "a)", "b)"). However, downstream
        # consumers (QuestionEnricher, M3 analysis) expect a "sub_question"
        # field. This block bridges that gap by copying "part" → "sub_question"
        # when "sub_question" is absent.
        cleaned_questions = []
        for q in parsed_questions:
            if isinstance(q, dict):
                if "sub_question" not in q and "part" in q:
                    q["sub_question"] = q["part"]
                cleaned_questions.append(q)

        return cleaned_questions