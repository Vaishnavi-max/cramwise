from app.schemas.recommendation import (
    RecommendationRequest
)


class RecommendationInputService:
    """
    M6.1 — Recommendation Input Service

    Responsible for:

        1. Validating raw student input.
        2. Normalizing the input.
        3. Converting it into a RecommendationRequest.

    IMPORTANT:

    The student gives a SUBJECT NAME, not a course code.

    Example:

        "Compiler Design"

    NOT:

        "BCS 306"

    Course-code resolution will happen through M2
    in the next step.

    This keeps M6 independent from internal database
    identifiers at the student-input level.

    M6.1 does NOT:

        - select topics
        - calculate importance
        - calculate study order
        - call Groq
        - perform RAG
    """

    # ======================================================
    # VALIDATE REQUEST
    # ======================================================

    def validate(
        self,
        request_data: dict,
    ) -> RecommendationRequest:
        """
        Validate raw student input.

        Example:

            Input:

            {
                "subject": "Compiler Design",
                "available_hours": 4
            }

            Output:

            RecommendationRequest(
                subject="Compiler Design",
                available_hours=4
            )
        """

        # --------------------------------------------------
        # BASIC TYPE CHECK
        # --------------------------------------------------

        if not isinstance(
            request_data,
            dict,
        ):

            raise TypeError(
                "Recommendation input must be a dictionary."
            )

        # --------------------------------------------------
        # PYDANTIC VALIDATION
        # --------------------------------------------------

        request = (
            RecommendationRequest.model_validate(
                request_data
            )
        )

        return request

    # ======================================================
    # CONVERT REQUEST TO DICTIONARY
    # ======================================================

    def to_dict(
        self,
        request: RecommendationRequest,
    ) -> dict:
        """
        Convert the validated Pydantic object into
        a normal Python dictionary.

        This will be useful for later M6 services.
        """

        return request.model_dump()