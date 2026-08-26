from pydantic import BaseModel, ConfigDict, Field


class ExampleSection(BaseModel):
    """
    Example used to make the topic easier to understand.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    problem: str = Field(
        ...,
        description="A simple example problem or scenario.",
    )

    explanation: str = Field(
        ...,
        description="Step-by-step explanation of the example.",
    )


class M65TopicExplanation(BaseModel):
    """
    M6.5 structured output.

    Responsibilities:
        - Explain the selected topic.
        - Provide important exam points.
        - Explain the topic step-by-step.
        - Provide a concrete example.
        - Connect the topic to relevant PYQs.
        - Optionally provide an exam tip.

    All fields are required at the JSON-schema level
    because Groq structured outputs require every
    property to appear in `required`.

    `exam_tip` is nullable, so Groq may return null
    when no additional exam tip is needed.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    # ======================================================
    # BASIC TOPIC
    # ======================================================

    topic: str = Field(
        ...,
        description="Name of the topic being explained.",
    )

    # ======================================================
    # CONCEPTUAL EXPLANATION
    # ======================================================

    explanation: str = Field(
        ...,
        description=(
            "Clear conceptual explanation of the topic "
            "for a student learning it from scratch."
        ),
    )

    # ======================================================
    # IMPORTANT POINTS
    # ======================================================

    key_points: list[str] = Field(
        ...,
        description=(
            "Important points the student should remember "
            "for exams."
        ),
    )

    # ======================================================
    # STEP-BY-STEP
    # ======================================================

    step_by_step: list[str] = Field(
        ...,
        description=(
            "Step-by-step explanation of the concept. "
            "Every item must be a plain string."
        ),
    )

    # ======================================================
    # EXAMPLE
    # ======================================================

    example: ExampleSection = Field(
        ...,
        description=(
            "A simple worked example of the selected topic."
        ),
    )

    # ======================================================
    # PYQ APPLICATION
    # ======================================================

    pyq_application: list[str] = Field(
        ...,
        description=(
            "Explanation of how the selected topic applies "
            "to the supplied previous-year questions. "
            "Each item should refer to an actual relevant "
            "PYQ and explain what concepts and changes are "
            "needed for that question."
        ),
    )

    # ======================================================
    # EXAM TIP
    # ======================================================

    exam_tip: str | None = Field(
        ...,
        description=(
            "Optional concise exam-oriented tip. "
            "Return null when no additional exam tip "
            "is needed."
        ),
    )