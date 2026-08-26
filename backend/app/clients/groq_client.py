import json
import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqClient:
    """
    Generic client responsible for communicating with Groq.

    IMPORTANT:
    This class knows NOTHING about:

        - PYQs
        - syllabus
        - topics
        - subtopics
        - prerequisites
        - importance

    Its only responsibility is:

        CramWise
            ↓
        GroqClient
            ↓
        Groq API
            ↓
        LLM response

    Academic/business logic lives in the respective
    services.
    """

    def __init__(
        self,
        model: str | None = None,
        max_completion_tokens: int = 6000,
        max_retries: int = 2,
        retry_delay: float = 2.0,
    ):
        """
        Initialize the Groq client.

        Parameters
        ----------
        model:
            Groq model to use.

        max_completion_tokens:
            Maximum number of tokens the model can generate.

        max_retries:
            Number of times to retry a failed API request.

        retry_delay:
            Seconds to wait between retries.
        """

        # ==================================================
        # API KEY
        # ==================================================

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set in the environment."
            )

        # ==================================================
        # MODEL
        # ==================================================

        self.model = (
            model
            or os.getenv("GROQ_MODEL")
            or "openai/gpt-oss-120b"
        )

        # ==================================================
        # SETTINGS
        # ==================================================

        self.max_completion_tokens = (
            max_completion_tokens
        )

        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # ==================================================
        # CREATE GROQ CLIENT
        # ==================================================

        self.client = Groq(
            api_key=api_key
        )

    # ======================================================
    # BASIC TEXT GENERATION
    # ======================================================

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a normal text-generation request to Groq.

        Returns:
            Model response as a string.
        """

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                response = (
                    self.client.chat.completions.create(
                        model=self.model,

                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt,
                            },
                            {
                                "role": "user",
                                "content": user_prompt,
                            },
                        ],

                        max_completion_tokens=(
                            self.max_completion_tokens
                        ),
                    )
                )

                content = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if content is None:

                    raise ValueError(
                        "Groq returned an empty response."
                    )

                return content.strip()

            except Exception as exc:

                if attempt >= self.max_retries:

                    raise RuntimeError(
                        "Groq API request failed after "
                        f"{self.max_retries + 1} attempts: "
                        f"{exc}"
                    ) from exc

                time.sleep(
                    self.retry_delay
                )

    # ======================================================
    # STRUCTURED JSON GENERATION
    # ======================================================

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        schema_name: str = "response",
    ) -> dict:
        """
        Send a request to Groq using strict structured output.

        The supplied JSON schema defines the exact structure
        expected from the model.

        The result is parsed into a Python dictionary.

        Pydantic validation is performed by the calling
        service.
        """

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                # ==========================================
                # API REQUEST
                # ==========================================

                response = (
                    self.client.chat.completions.create(
                        model=self.model,

                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt,
                            },
                            {
                                "role": "user",
                                "content": user_prompt,
                            },
                        ],

                        max_completion_tokens=(
                            self.max_completion_tokens
                        ),

                        # ==================================
                        # STRICT STRUCTURED OUTPUT
                        # ==================================
                        #
                        # Previously we had:
                        #
                        # "name": schema_name,
                        # "schema": json_schema
                        #
                        # Now we explicitly tell Groq
                        # to enforce the schema.
                        #

                        response_format={
                            "type": "json_schema",

                            "json_schema": {
                                "name": schema_name,

                                "strict": True,

                                "schema": json_schema,
                            },
                        },
                    )
                )

                # ==========================================
                # EXTRACT RESPONSE
                # ==========================================

                content = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if content is None:

                    raise ValueError(
                        "Groq returned an empty JSON response."
                    )

                # ==========================================
                # STRING → PYTHON DICT
                # ==========================================

                result = json.loads(
                    content
                )

                if not isinstance(
                    result,
                    dict,
                ):

                    raise ValueError(
                        "Expected Groq JSON response "
                        "to be an object."
                    )

                return result

            except Exception as exc:

                # ==========================================
                # FINAL ATTEMPT
                # ==========================================

                if attempt >= self.max_retries:

                    raise RuntimeError(
                        "Groq structured-output request "
                        "failed after "
                        f"{self.max_retries + 1} attempts: "
                        f"{exc}"
                    ) from exc

                # ==========================================
                # RETRY
                # ==========================================

                time.sleep(
                    self.retry_delay
                )