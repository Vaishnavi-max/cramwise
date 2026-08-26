import asyncio

from app.services.m6_5.topic_explanation_service import (
    M65TopicExplanationService,
)


async def main():

    print("=" * 65)
    print("CRAMWISE — M6.5 TOPIC EXPLANATION TEST")
    print("=" * 65)

    # --------------------------------------------------
    # TEST TOPIC
    # --------------------------------------------------

    topic_id = "BCS306_U2_T02_S03"

    topic = "Bottom-Up Parsing"

    subtopic = (
        "Constructing Canonical LR parsing tables"
    )

    course_code = "BCS 306"

    unit = 2

    print(f"\nTopic ID: {topic_id}")
    print(f"Topic: {topic}")
    print(f"Subtopic: {subtopic}")
    print(f"Course: {course_code}")
    print(f"Unit: {unit}")

    # --------------------------------------------------
    # CREATE SERVICE
    # --------------------------------------------------

    service = M65TopicExplanationService(
        cognee_top_k=5,
        pyq_top_k=3,
    )

    print("\nM6.5 service created.")

    # --------------------------------------------------
    # GENERATE
    # --------------------------------------------------

    print(
        "\n--- GENERATING M6.5 EXPLANATION ---"
    )

    result = await service.generate_explanation(
        topic_id=topic_id,
        topic=topic,
        subtopic=subtopic,
        course_code=course_code,
        unit=unit,
    )

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------

    print(
        "\n========== M6.5 RESULT =========="
    )

    print(result)

    # --------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------

    # M6.5 now returns natural-language text,
    # NOT a structured Pydantic/JSON object.

    assert isinstance(
        result,
        str,
    ), (
        "M6.5 response must be a string."
    )

    assert result.strip(), (
        "M6.5 returned an empty response."
    )

    # --------------------------------------------------
    # TOPIC VALIDATION
    # --------------------------------------------------

    # LLMs may use different Unicode dash characters:
    #
    #   Bottom-Up Parsing
    #   Bottom-Up Parsing
    #   Bottom–Up Parsing
    #   Bottom—Up Parsing
    #
    # Therefore, normalize dash characters before
    # checking whether the topic appears in the response.

    def normalize_text(text: str) -> str:

        return (
            text.lower()
            .replace("-", " ")
            .replace("‐", " ")
            .replace("-", " ")
            .replace("‒", " ")
            .replace("–", " ")
            .replace("—", " ")
            .replace("―", " ")
        )

    normalized_topic = normalize_text(
        topic
    )

    normalized_result = normalize_text(
        result
    )

    topic_words = (
        normalized_topic.split()
    )

    assert all(
        word in normalized_result
        for word in topic_words
    ), (
        "Generated response does not mention "
        "the selected topic."
    )

    # --------------------------------------------------
    # RESPONSE LENGTH VALIDATION
    # --------------------------------------------------

    # M6.5 is supposed to produce a complete
    # teaching explanation, so an extremely short
    # response indicates a generation problem.

    assert len(
        result.strip()
    ) >= 200, (
        "M6.5 response is unexpectedly short."
    )

    # --------------------------------------------------
    # BASIC CONTENT VALIDATION
    # --------------------------------------------------

    normalized_result_lower = (
        normalized_result
    )

    # The response should contain at least some
    # teaching-oriented content.

    teaching_keywords = [
        "explain",
        "parsing",
        "closure",
        "goto",
        "action",
        "reduce",
        "shift",
    ]

    found_keywords = [
        keyword
        for keyword in teaching_keywords
        if keyword in normalized_result_lower
    ]

    assert len(
        found_keywords
    ) >= 2, (
        "Generated response does not appear "
        "to contain sufficient topic-specific "
        "teaching content."
    )

    # --------------------------------------------------
    # SUCCESS MESSAGES
    # --------------------------------------------------

    print(
        "\n✓ Natural-language explanation exists."
    )

    print(
        "✓ Response is a string."
    )

    print(
        "✓ Selected topic appears in the response."
    )

    print(
        "✓ Unicode punctuation differences "
        "do not affect topic validation."
    )

    print(
        "✓ Response contains sufficient content."
    )

    print(
        "✓ Topic-specific teaching content exists."
    )

    print(
        "✓ M6.5 no longer requires structured JSON."
    )

    print(
        "\n" + "=" * 65
    )

    print(
        "M6.5 TEST PASSED"
    )

    print(
        "=" * 65
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )