from app.clients.groq_client import GroqClient


def main():

    # ======================================================
    # TEST 1 — CREATE CLIENT
    # ======================================================

    print(
        "Creating Groq client..."
    )

    client = GroqClient()

    print(
        "Groq client created successfully."
    )

    print(
        f"Model: {client.model}"
    )

    # ======================================================
    # TEST 2 — BASIC TEXT GENERATION
    # ======================================================

    print(
        "\n--- TEST 2: BASIC GENERATION ---"
    )

    response = client.generate(
        system_prompt=(
            "You are a concise assistant. "
            "Answer only what is asked."
        ),

        user_prompt=(
            "What is 2 + 2? "
            "Answer with only the number."
        ),
    )

    print(
        f"LLM response: {response}"
    )

    # ======================================================
    # TEST 3 — STRUCTURED JSON GENERATION
    # ======================================================

    print(
        "\n--- TEST 3: STRUCTURED JSON ---"
    )

    # This is a tiny schema just to verify that
    # structured output works.
    #
    # Later M4 will replace this with our actual
    # QuestionAnalysis schema.

    test_schema = {
        "type": "object",

        "properties": {
            "answer": {
                "type": "string"
            },

            "number": {
                "type": "integer"
            },
        },

        "required": [
            "answer",
            "number"
        ],

        "additionalProperties": False,
    }

    structured_response = (
        client.generate_json(

            system_prompt=(
                "You are a structured data generator. "
                "Return exactly the requested JSON."
            ),

            user_prompt=(
                "Return the answer to 2 + 2. "
                "The answer should be 4."
            ),

            json_schema=test_schema,

            schema_name="simple_math",
        )
    )

    print(
        "Structured response:"
    )

    print(
        structured_response
    )

    # ======================================================
    # TEST 4 — VERIFY RESULT
    # ======================================================

    print(
        "\n--- TEST 4: VALIDATION ---"
    )

    # Check that the response is actually a dictionary.

    assert isinstance(
        structured_response,
        dict
    )

    # Check required fields.

    assert "answer" in structured_response
    assert "number" in structured_response

    # The model should return 4.
    #
    # We don't need to make the test dependent on
    # exact wording of "answer", but the number should
    # be correct.

    assert (
        structured_response["number"] == 4
    )

    print(
        "Structured output validation passed."
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    print(
        "\nM3 Groq Client tests passed successfully."
    )


if __name__ == "__main__":
    main()