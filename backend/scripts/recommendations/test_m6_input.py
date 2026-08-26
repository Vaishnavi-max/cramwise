from app.services.recommendations.recommendation_input_service import (
    RecommendationInputService
)


# ==========================================================
# TEST
# ==========================================================

def main():

    print(
        "=" * 65
    )

    print(
        "M6.1 — RECOMMENDATION INPUT TEST"
    )

    print(
        "=" * 65
    )

    service = (
        RecommendationInputService()
    )

    # ======================================================
    # TEST 1 — BASIC STUDENT REQUEST
    # ======================================================

    print(
        "\n--- TEST 1: BASIC STUDENT REQUEST ---"
    )

    request = service.validate(
        {
            "subject": "Compiler design",
            "available_hours": 6,
        }
    )

    print(
        request
    )

    assert (
        request.subject
        == "Compiler design"
    )

    assert (
        request.available_hours
        == 6
    )

    print(
        "Basic student request validation passed."
    )

    # ======================================================
    # TEST 2 — SUBJECT NAME NORMALIZATION
    # ======================================================

    print(
        "\n--- TEST 2: SUBJECT NORMALIZATION ---"
    )

    request = service.validate(
        {
            "subject": "   Compiler   Design   ",
            "available_hours": 3.5,
        }
    )

    print(
        request
    )

    # Multiple spaces should be removed.

    assert (
        request.subject
        == "Compiler Design"
    )

    print(
        "Subject normalization passed."
    )

    # ======================================================
    # TEST 3 — EXAM TYPE NORMALIZATION
    # ======================================================

    print(
        "\n--- TEST 3: EXAM TYPE ---"
    )

    request = service.validate(
        {
            "subject": "Compiler Design",
            "available_hours": 4,
            "exam_type": " endterm ",
        }
    )

    print(
        request
    )

    assert (
        request.exam_type
        == "ENDTERM"
    )

    print(
        "Exam type normalization passed."
    )

    # ======================================================
    # TEST 4 — COMPLETED TOPICS
    # ======================================================

    print(
        "\n--- TEST 4: COMPLETED TOPICS ---"
    )

    request = service.validate(
        {
            "subject": "Compiler Design",
            "available_hours": 2,
            "completed_topics": [
                "BCS306_U1_T01_S01",
                "BCS306_U1_T01_S02",
                "BCS306_U1_T01_S01",
                " ",
            ],
        }
    )

    print(
        request
    )

    assert (
        request.completed_topics
        == [
            "BCS306_U1_T01_S01",
            "BCS306_U1_T01_S02",
        ]
    )

    print(
        "Completed-topic validation passed."
    )

    # ======================================================
    # TEST 5 — INVALID HOURS
    # ======================================================

    print(
        "\n--- TEST 5: INVALID HOURS ---"
    )

    try:

        service.validate(
            {
                "subject": "Compiler Design",
                "available_hours": 0,
            }
        )

        raise AssertionError(
            "Zero hours should have failed."
        )

    except ValueError:

        print(
            "Invalid hours correctly rejected."
        )

    # ======================================================
    # TEST 6 — INVALID EXAM TYPE
    # ======================================================

    print(
        "\n--- TEST 6: INVALID EXAM TYPE ---"
    )

    try:

        service.validate(
            {
                "subject": "Compiler Design",
                "available_hours": 4,
                "exam_type": "FINAL",
            }
        )

        raise AssertionError(
            "Invalid exam type should have failed."
        )

    except ValueError:

        print(
            "Invalid exam type correctly rejected."
        )

    # ======================================================
    # TEST 7 — EMPTY SUBJECT
    # ======================================================

    print(
        "\n--- TEST 7: EMPTY SUBJECT ---"
    )

    try:

        service.validate(
            {
                "subject": "   ",
                "available_hours": 4,
            }
        )

        raise AssertionError(
            "Empty subject should have failed."
        )

    except ValueError:

        print(
            "Empty subject correctly rejected."
        )

    # ======================================================
    # TEST 8 — DICTIONARY CONVERSION
    # ======================================================

    print(
        "\n--- TEST 8: DICTIONARY CONVERSION ---"
    )

    request = service.validate(
        {
            "subject": "Compiler Design",
            "available_hours": 4,
        }
    )

    result = service.to_dict(
        request
    )

    print(
        result
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result["subject"]
        == "Compiler Design"
    )

    assert (
        result["available_hours"]
        == 4
    )

    print(
        "Dictionary conversion passed."
    )

    # ======================================================
    # TEST 9 — REALISTIC STUDENT REQUEST
    # ======================================================

    print(
        "\n--- TEST 9: REALISTIC STUDENT REQUEST ---"
    )

    request = service.validate(
        {
            "subject": "compiler design",
            "available_hours": 5,
            "exam_type": "endterm",
            "completed_topics": [
                "BCS306_U1_T01_S01",
            ],
        }
    )

    print(
        "\nNormalized request:"
    )

    print(
        request
    )

    assert (
        request.subject
        == "compiler design"
    )

    assert (
        request.exam_type
        == "ENDTERM"
    )

    print(
        "Realistic student request passed."
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    print(
        "\n" + "=" * 65
    )

    print(
        "M6.1 Recommendation Input "
        "tests passed successfully."
    )

    print(
        "=" * 65
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()