from app.clients.groq_client import GroqClient

from app.services.llm_analysis.syllabus_catalog_service import (
    SyllabusCatalogService
)

from app.prompts.question_analysis_prompt import (
    SYSTEM_PROMPT,
    build_user_prompt
)

from app.schemas.llm_analysis import (
    QuestionAnalysis
)


class QuestionAnalysisService:
    """
    Main service responsible for analyzing ONE PYQ.

    Pipeline:

        Question
            ↓
        M2 Syllabus Catalog
            ↓
        Relevant Unit Candidates
            ↓
        Prompt Builder
            ↓
        M3 Groq Client
            ↓
        Structured JSON
            ↓
        Pydantic Validation
            ↓
        Validate syllabus IDs
            ↓
        Retrieve canonical syllabus record
            ↓
        Final analysis result
    """

    def __init__(
        self,
        catalog: SyllabusCatalogService,
        groq_client: GroqClient,
    ):
        """
        Receive the M2 syllabus catalog and M3 Groq client.
        """

        self.catalog = catalog
        self.groq_client = groq_client

    # ======================================================
    # ANALYZE ONE QUESTION
    # ======================================================

    def analyze(
        self,
        question: dict
    ) -> dict:
        """
        Analyze one PYQ.

        Returns a dictionary containing:

            topic_id
            topic
            subtopic
            is_independent
            prerequisites
            evidence

        The topic and subtopic come from the syllabus
        catalog, NOT from the LLM.
        """

        # --------------------------------------------------
        # STEP 1 — QUESTION CONTEXT
        # --------------------------------------------------

        course_code = question["subject_code"]
        unit_number = question["unit"]

        # --------------------------------------------------
        # STEP 2 — GET UNIT SYLLABUS
        # --------------------------------------------------

        unit_candidates = (
            self.catalog.get_unit_catalog(
                course_code,
                unit_number
            )
        )

        if not unit_candidates:

            raise ValueError(
                f"No syllabus records found for "
                f"{course_code}, Unit {unit_number}."
            )

        # --------------------------------------------------
        # STEP 3 — BUILD PROMPT
        # --------------------------------------------------

        user_prompt = build_user_prompt(
            question=question,
            unit_candidates=unit_candidates,
        )

        # --------------------------------------------------
        # STEP 4 — STRUCTURED OUTPUT SCHEMA
        # --------------------------------------------------

        json_schema = (
            QuestionAnalysis.model_json_schema()
        )

        # --------------------------------------------------
        # STEP 5 — CALL GROQ
        # --------------------------------------------------

        raw_result = (
            self.groq_client.generate_json(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                json_schema=json_schema,
                schema_name="question_analysis",
            )
        )

        # --------------------------------------------------
        # STEP 6 — PYDANTIC VALIDATION
        # --------------------------------------------------

        analysis = (
            QuestionAnalysis.model_validate(
                raw_result
            )
        )

        # --------------------------------------------------
        # STEP 7 — VALIDATE IDS
        # --------------------------------------------------

        self._validate_analysis(
            analysis=analysis,
            unit_candidates=unit_candidates,
        )

        # --------------------------------------------------
        # STEP 8 — GET CANONICAL SYLLABUS RECORD
        # --------------------------------------------------

        selected_record = next(
            record
            for record in unit_candidates
            if record["index_id"]
            == analysis.topic_id
        )

        # --------------------------------------------------
        # STEP 9 — RETURN FINAL RESULT
        # --------------------------------------------------

        return {
            "topic_id": analysis.topic_id,

            # These values come from OUR syllabus,
            # not from generated LLM text.
            "topic": selected_record["topic"],
            "subtopic": selected_record["subtopic"],

            "is_independent": (
                analysis.is_independent
            ),

            "prerequisites": (
                analysis.prerequisites
            ),

            "evidence": analysis.evidence,
        }

    # ======================================================
    # VALIDATE LLM RESULT
    # ======================================================

    def _validate_analysis(
        self,
        analysis: QuestionAnalysis,
        unit_candidates: list[dict],
    ) -> None:
        """
        Validate all syllabus IDs returned by the LLM.

        The LLM is allowed to select IDs.

        The LLM is NOT allowed to invent IDs.
        """

        # --------------------------------------------------
        # VALID SYLLABUS IDS
        # --------------------------------------------------

        valid_ids = {
            record["index_id"]
            for record in unit_candidates
        }

        # --------------------------------------------------
        # SELECTED TOPIC
        # --------------------------------------------------

        if analysis.topic_id not in valid_ids:

            raise ValueError(
                "LLM returned an invalid topic_id: "
                f"{analysis.topic_id}"
            )

        # --------------------------------------------------
        # PREREQUISITES
        # --------------------------------------------------

        for prerequisite_id in (
            analysis.prerequisites
        ):

            if prerequisite_id not in valid_ids:

                raise ValueError(
                    "LLM returned an invalid "
                    "prerequisite ID: "
                    f"{prerequisite_id}"
                )

        # --------------------------------------------------
        # SELF-DEPENDENCY
        # --------------------------------------------------

        if (
            analysis.topic_id
            in analysis.prerequisites
        ):

            raise ValueError(
                "A topic cannot be its own prerequisite."
            )