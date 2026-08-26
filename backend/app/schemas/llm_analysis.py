from pydantic import BaseModel, Field


class QuestionAnalysis(BaseModel):
    """
    Structured output produced by the LLM for ONE PYQ.

    IMPORTANT DESIGN DECISION:

    The LLM only selects the syllabus record using its
    unique index_id.

    It does NOT generate the topic/subtopic names.

    Why?

    Because the syllabus catalog is our source of truth.

    Example:

        LLM returns:

            topic_id = BCS302_U2_T01_S05

        CramWise then looks up that ID and gets:

            topic    = Network Protocols
            subtopic = Hybrid routing protocols

    This prevents free-text mismatches between the LLM
    and our syllabus catalog.
    """

    # ------------------------------------------------------
    # SELECTED SYLLABUS RECORD
    # ------------------------------------------------------

    topic_id: str = Field(
        description=(
            "The index_id of the syllabus record that "
            "best matches the question."
        )
    )

    # ------------------------------------------------------
    # DEPENDENCY INFORMATION
    # ------------------------------------------------------

    is_independent: bool = Field(
        description=(
            "True if the selected topic can reasonably "
            "be studied independently. False if understanding "
            "other topics first is important."
        )
    )

    prerequisites: list[str] = Field(
        default_factory=list,
        description=(
            "Syllabus index_ids of topics that should "
            "ideally be understood before studying the "
            "selected topic."
        )
    )

    # ------------------------------------------------------
    # EXPLANATION
    # ------------------------------------------------------

    evidence: str = Field(
        description=(
            "A short explanation of why the selected "
            "syllabus record matches the question and, "
            "if applicable, why prerequisites are needed."
        )
    )