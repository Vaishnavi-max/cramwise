from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()


print("=" * 70)
print("GROQ CONNECTION TEST")
print("=" * 70)


api_key = os.getenv("GROQ_API_KEY")

print(
    f"API key loaded: {bool(api_key)}"
)


if not api_key:

    print("\nERROR: GROQ_API_KEY not found.")

    raise SystemExit(1)


client = Groq(
    api_key=api_key
)


print("\nSending simple test request...\n")


try:

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ_OK",
            }
        ],

        temperature=0,

        max_completion_tokens=512,
        reasoning_effort="low",
    )

    choice = response.choices[0]

    print("\n" + "=" * 70)
    print("GROQ RESPONSE DEBUG")
    print("=" * 70)

    print(
        "\nFinish reason:"
    )

    print(
        choice.finish_reason
    )

    print(
        "\nMessage:"
    )

    print(
        choice.message
    )

    print(
        "\nContent:"
    )

    print(
        repr(choice.message.content)
    )

    print(
        "\nUsage:"
    )

    print(
        response.usage
    )

    print("\n" + "=" * 70)

except Exception as e:

    print("=" * 70)
    print("FAILED")
    print("=" * 70)

    print(
        f"\nError type: {type(e).__name__}"
    )

    print(
        f"Error: {e}"
    )