from typing import Any

import cognee
from cognee.modules.search.types import SearchType


class CogneeService:
    """
    CramWise wrapper around Cognee 1.5.1.

    Responsibility:
        - add academic content to Cognee
        - retrieve relevant academic chunks

    CramWise architecture:

        Notes / Syllabus / PYQs
                    |
                    v
              Cognee remember()
                    |
                    v
             Vector + Graph
                    |
                    v
              Cognee recall()
                    |
                    v
             Relevant chunks
                    |
                    v
                  M6.5
                    |
                    v
              Groq LLM
                    |
                    v
        Explanation + Examples +
        PYQ Application

    This service does NOT:
        - decide topic importance
        - calculate priority
        - generate study plans
        - generate the final student explanation
        - call Groq directly

    IMPORTANT:
        Cognee is used as the KNOWLEDGE/RETRIEVAL layer.

        We intentionally do NOT use:
            GRAPH_COMPLETION_COT

        because that can trigger additional LLM reasoning
        and follow-up questions.

        Instead we use:
            SearchType.CHUNKS

        so M6.5 receives relevant academic context and
        our own Groq service generates the final answer.
    """

    def __init__(
        self,
        dataset_name: str = "cramwise_default",
    ):
        self.dataset_name = dataset_name

    # ======================================================
    # DATASET
    # ======================================================

    @staticmethod
    def make_dataset_name(
        course_code: str,
    ) -> str:
        """
        Convert course code into a stable
        CramWise Cognee dataset name.

        Example:

            BCS 306
                ↓
            cramwise_BCS306
        """

        normalized = "".join(
            course_code.strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                "Course code cannot be empty."
            )

        return f"cramwise_{normalized}"

    # ======================================================
    # REMEMBER
    # ======================================================

    async def add_content(
        self,
        content: str | list[str],
        dataset_name: str | None = None,
        chunk_size: int | None = None,
    ) -> Any:
        """
        Add academic content to Cognee.

        Content can be:
            - one string
            - multiple strings

        Cognee 1.5.1:
            remember(...)

        Cognee handles:
            - ingestion
            - chunking
            - embeddings
            - vector indexing
            - knowledge graph construction
        """

        # --------------------------------------------------
        # VALIDATE CONTENT
        # --------------------------------------------------

        if isinstance(content, str):

            if not content.strip():
                raise ValueError(
                    "Content cannot be empty."
                )

        elif isinstance(content, list):

            if not content:
                raise ValueError(
                    "Content list cannot be empty."
                )

            for item in content:

                if (
                    not isinstance(item, str)
                    or not item.strip()
                ):
                    raise ValueError(
                        "Every content item "
                        "must be a non-empty string."
                    )

        else:

            raise TypeError(
                "Content must be a string "
                "or list of strings."
            )

        # --------------------------------------------------
        # DATASET
        # --------------------------------------------------

        target_dataset = (
            dataset_name
            or self.dataset_name
        )

        # --------------------------------------------------
        # COGNEE REMEMBER
        # --------------------------------------------------

        kwargs = {
            "data": content,
            "dataset_name": target_dataset,
            "run_in_background": False,
        }

        if chunk_size is not None:
            kwargs["chunk_size"] = chunk_size

        result = await cognee.remember(
            **kwargs
        )

        return result

    # ======================================================
    # RECALL
    # ======================================================

    async def search(
        self,
        query: str,
        dataset_name: str | None = None,
        top_k: int = 5,
        only_context: bool = True,
    ) -> list[Any]:
        """
        Retrieve relevant academic chunks from Cognee.

        IMPORTANT:

        CramWise intentionally uses:

            SearchType.CHUNKS

        instead of:

            GRAPH_COMPLETION_COT

        Why?

        GRAPH_COMPLETION_COT can perform additional
        LLM reasoning and generate follow-up questions.

        That causes unnecessary token usage and can hit
        the Groq TPM limit.

        CramWise wants:

            Query
              ↓
            Cognee
              ↓
            Relevant academic chunks
              ↓
            M6.5
              ↓
            Groq
              ↓
            Final explanation

        Therefore Cognee is responsible for RETRIEVAL,
        while M6.5 is responsible for GENERATION.
        """

        # --------------------------------------------------
        # VALIDATE QUERY
        # --------------------------------------------------

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        # --------------------------------------------------
        # DATASET
        # --------------------------------------------------

        target_dataset = (
            dataset_name
            or self.dataset_name
        )

        # --------------------------------------------------
        # RETRIEVAL-ONLY RECALL
        # --------------------------------------------------

        results = await cognee.recall(
            query_text=query.strip(),

            # IMPORTANT:
            # Retrieve chunks only.
            #
            # This prevents Cognee from selecting
            # GRAPH_COMPLETION_COT for this request.
            query_type=SearchType.CHUNKS,

            datasets=[
                target_dataset
            ],

            # Keep the retrieved context controlled.
            top_k=top_k,

            # Do not allow Cognee's automatic router
            # to override SearchType.CHUNKS.
            auto_route=False,

            # Return retrieved context instead of asking
            # Cognee to generate the final answer.
            only_context=True,
        )

        return results