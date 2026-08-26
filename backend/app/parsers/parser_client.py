import json
import re
import time
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class ParserClient:

    def __init__(
        self,
        model="openai/gpt-oss-120b",
    ):
        """
        Initialize the Groq client.

        model:
            Groq model to use for parsing.
        """

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = model

    def parse(
        self,
        text: str,
        prompt: str,
    ):
        
        print(f"\nSending request to {self.model}...\n")
        
        print("\n========== TOKEN DEBUG ==========")
        print("Prompt characters:", len(prompt))
        print("OCR characters:", len(text))
        print("Total characters:", len(prompt) + len(text))
        print(
            "Approx input tokens:",
            (len(prompt) + len(text)) // 4
        )
        print("=================================\n")
        

        # ------------------------------------
        # Retry up to 2 times
        # ------------------------------------

        response = None

        for attempt in range(2):

            try:

                response = self.client.chat.completions.create(

                    model=self.model,

                    messages=[
                        {
                            "role": "user",
                            "content": f"{prompt}\n\n{text}",
                        }
                    ],

                    temperature=0,
                    max_completion_tokens=6000,
                    reasoning_effort="low",
                )

                print("Response received.\n")
                break

            except Exception as e:

                print(f"\nAttempt {attempt + 1} failed.")
                print(type(e).__name__)
                print(e)

                if attempt == 1:
                    print("\n========== GROQ ERROR ==========")
                    raise

                print("Waiting 5 seconds and retrying...\n")
                time.sleep(5)

        print(
            f"Finish reason: "
            f"{response.choices[0].finish_reason}"
        )

        print(
            f"Completion tokens: "
            f"{response.usage.completion_tokens}"
        )
        # ------------------------------------
        # Get model response
        # ------------------------------------

        result = response.choices[0].message.content.strip()

        # ------------------------------------
        # Remove markdown if present
        # ------------------------------------

        result = re.sub(
            r"^```(?:json)?\s*",
            "",
            result,
        )

        result = re.sub(
            r"\s*```$",
            "",
            result,
        )

        # ------------------------------------
        # Print FULL raw response
        # ------------------------------------

        print("\n" + "=" * 80)
        print("FULL RAW MODEL RESPONSE")
        print("=" * 80)
        print(result)
        print("=" * 80 + "\n")

        # ------------------------------------
        # Save raw response
        # ------------------------------------

        with open(
            "parser_debug_output.txt",
            "w",
            encoding="utf-8",
        ) as f:

            f.write(result)

        # ------------------------------------
        # Parse JSON
        # ------------------------------------

        try:

            return json.loads(result)

        except json.JSONDecodeError:

            print("\n===== JSON PARSE FAILED =====\n")

            fixed_result = re.sub(
                r'"co"\s*:\s*"([^"]+)"\s*&\s*"([^"]+)"',
                r'"co": ["\1", "\2"]',
                result,
            )

            if fixed_result != result:

                print("Attempting automatic JSON repair...\n")

                try:
                    return json.loads(fixed_result)

                except json.JSONDecodeError:
                    pass

            print("\n===== RAW MODEL OUTPUT =====")
            print(result)
            print("============================\n")

            raise ValueError(
                "Model did not return valid JSON."
            )