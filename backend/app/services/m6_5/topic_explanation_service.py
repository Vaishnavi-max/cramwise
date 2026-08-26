from typing import Any

from app.clients.groq_client import GroqClient

from app.prompts.m6_5_topic_explanation_prompt import (
    M65_SYSTEM_PROMPT,
    build_m65_user_prompt,
)

from app.services.cognee_service import (
    CogneeService,
)

from app.services.m6_5.pyq_retrieval_service import (
    M65PyqRetrievalService,
)


class M65TopicExplanationService:
    """
    M6.5 — Topic Explanation + PYQ Application.

    Responsibilities:

        1. Receive selected topic from M6.4.
        2. Retrieve relevant notes from Cognee.
        3. Retrieve relevant enriched PYQs.
        4. Build a grounded teaching prompt.
        5. Ask Groq to generate a natural-language explanation.
        6. Return the generated explanation as text.

    This service does NOT:

        - select study topics
        - calculate priority
        - create study plans
        - OCR PDFs
        - parse raw PYQs
        - store knowledge in Cognee
        - generate structured JSON
    """

    def __init__(
        self,
        cognee_service: CogneeService | None = None,
        pyq_service: M65PyqRetrievalService | None = None,
        groq_client: GroqClient | None = None,
        cognee_top_k: int = 5,
        pyq_top_k: int = 3,
    ):
        self.cognee_service = (
            cognee_service
            or CogneeService()
        )

        self.pyq_service = (
            pyq_service
            or M65PyqRetrievalService()
        )

        self.groq_client = (
            groq_client
            or GroqClient(
                max_completion_tokens=3500,
                max_retries=1,
                retry_delay=2.0,
            )
        )

        self.cognee_top_k = cognee_top_k
        self.pyq_top_k = pyq_top_k

    # ======================================================
    # MAIN METHOD
    # ======================================================

    async def generate_explanation(
        self,
        *,
        topic_id: str,
        topic: str,
        subtopic: str | None,
        course_code: str,
        unit: int,
    ) -> str:
        """
        Generate a complete M6.5 explanation.

        Returns
        -------
        str
            Natural-language explanation suitable for
            displaying directly in the CramWise chat UI.
        """

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not topic or not topic.strip():
            raise ValueError(
                "topic cannot be empty."
            )

        if not course_code or not course_code.strip():
            raise ValueError(
                "course_code cannot be empty."
            )

        if int(unit) <= 0:
            raise ValueError(
                "unit must be greater than zero."
            )

        # --------------------------------------------------
        # DATASET
        # --------------------------------------------------

        dataset_name = (
            CogneeService.make_dataset_name(
                course_code
            )
        )

        # ==================================================
        # STEP 1 — COGNEE RETRIEVAL
        # ==================================================

        query_parts = [
            topic.strip(),
        ]

        if subtopic and subtopic.strip():
            query_parts.append(
                subtopic.strip()
            )

        query_parts.append(
            f"unit {unit}"
        )

        query = " ".join(
            query_parts
        )

        print(
            "\n[M6.5] Retrieving academic context "
            "from Cognee..."
        )

        cognee_results = (
            await self.cognee_service.search(
                query=query,
                dataset_name=dataset_name,
                top_k=self.cognee_top_k,
                only_context=True,
            )
        )

        cognee_context = (
            self._extract_cognee_context(
                cognee_results
            )
        )

        print(
            "[M6.5] Cognee chunks retrieved: "
            f"{len(cognee_context)}"
        )

        # ==================================================
        # STEP 2 — PYQ RETRIEVAL
        # ==================================================

        print(
            "[M6.5] Retrieving relevant PYQs..."
        )

        pyqs = (
            self.pyq_service.retrieve(
                course_code=course_code,
                unit=unit,
                topic=topic,
                subtopic=subtopic,
                top_k=self.pyq_top_k,
            )
        )

        print(
            "[M6.5] Relevant PYQs retrieved: "
            f"{len(pyqs)}"
        )

        # ==================================================
        # STEP 3 — BUILD GROUNDED PROMPT
        # ==================================================

        user_prompt = (
            build_m65_user_prompt(
                topic=topic,
                subtopic=subtopic,
                course_code=course_code,
                unit=unit,
                cognee_context=cognee_context,
                pyqs=pyqs,
            )
        )

        # ==================================================
        # STEP 4 — GROQ TEXT GENERATION
        # ==================================================

        print(
            "[M6.5] Sending natural-language request "
            "to Groq..."
        )

        try:

            result = self.groq_client.generate(
                system_prompt=M65_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

        except Exception as exc:

            print(
                "\n[M6.5] Groq generation failed."
            )

            raise RuntimeError(
                "M6.5 failed to generate the topic "
                "explanation."
            ) from exc

        # ==================================================
        # STEP 5 — BASIC RESPONSE VALIDATION
        # ==================================================

        if not result or not result.strip():

            raise ValueError(
                "M6.5 received an empty response from Groq."
            )

        result = result.strip()

        print(
            "[M6.5] Groq response received."
        )

        print(
            "[M6.5] Natural-language response length: "
            f"{len(result)} characters."
        )

        # ==================================================
        # SUCCESS
        # ==================================================

        return result

    # ======================================================
    # COGNEE RESULT EXTRACTION
    # ======================================================

    @staticmethod
    def _extract_cognee_context(
        results: list[Any],
    ) -> list[str]:
        """
        Convert Cognee CHUNKS results into plain text.
        """

        context: list[str] = []

        for result in results:

            text = None

            # ------------------------------------------------
            # Cognee response object
            # ------------------------------------------------

            if hasattr(
                result,
                "text",
            ):

                text = getattr(
                    result,
                    "text",
                )

            # ------------------------------------------------
            # Dictionary response
            # ------------------------------------------------

            elif isinstance(
                result,
                dict,
            ):

                text = (
                    result.get("text")
                    or result.get("value")
                )

            # ------------------------------------------------
            # Keep only valid text
            # ------------------------------------------------

            if (
                isinstance(
                    text,
                    str,
                )
                and text.strip()
            ):

                context.append(
                    text.strip()
                )

        return context