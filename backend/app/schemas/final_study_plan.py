from pydantic import BaseModel, Field


# ==========================================================
# FINAL STUDY SESSION
# ==========================================================


class StudySession(BaseModel):
    """
    One topic/session in the final student study plan.
    """

    study_order: int = Field(
        ge=1,
        description="Order in which the topic should be studied."
    )

    topic_id: str = Field(
        min_length=1,
        description="Validated syllabus topic ID."
    )

    topic: str = Field(
        min_length=1,
        description="Human-readable topic name."
    )

    subtopic: str | None = Field(
        default=None,
        description="Human-readable subtopic."
    )

    unit: int = Field(
        ge=1,
        description="Syllabus unit."
    )

    recommended_minutes: int = Field(
        gt=0,
        description="Final recommended study time."
    )

    importance_score: float = Field(
        ge=0
    )

    priority: str = Field(
        min_length=1
    )

    prerequisites: list[str] = Field(
        default_factory=list
    )

    reason: str = Field(
        min_length=1
    )


# ==========================================================
# FINAL STUDY PLAN
# ==========================================================


class FinalStudyPlan(BaseModel):
    """
    M6.4 — Final validated study plan.

    This is the final structured output that can be
    consumed by the frontend.
    """

    subject: str = Field(
        min_length=1
    )

    course_code: str = Field(
        min_length=1
    )

    available_minutes: int = Field(
        gt=0
    )

    total_planned_minutes: int = Field(
        ge=0
    )

    sessions: list[StudySession] = Field(
        default_factory=list
    )

    validation_status: str = Field(
        default="VALID"
    )