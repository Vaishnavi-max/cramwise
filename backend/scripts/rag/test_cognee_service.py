import asyncio

from app.services.cognee_service import (
    CogneeService,
)


# ==========================================================
# TEST DATA
# ==========================================================

TEST_DATA = """
Compiler Design is the study of techniques used
to translate a high-level programming language
into a target language.

A compiler generally consists of several phases,
including lexical analysis, syntax analysis,
semantic analysis, intermediate code generation,
code optimization, and code generation.

Bottom-Up Parsing constructs a parse tree starting
from the input symbols and gradually combines them
towards the start symbol.

LR parsing is a bottom-up parsing technique.
Canonical LR parsing tables use LR items, closure,
GOTO, ACTION and GOTO tables.

The lexical analyzer converts a stream of characters
into tokens.
"""


# ==========================================================
# TEST
# ==========================================================

async def main():

    print("=" * 65)

    print(
        "CRAMWISE — COGNEE SERVICE TEST"
    )

    print("=" * 65)

    # ------------------------------------------------------
    # STEP 1 — CREATE SERVICE
    # ------------------------------------------------------

    dataset_name = (
        CogneeService.make_dataset_name(
            "BCS 306"
        )
    )

    print(
        f"\nDataset: {dataset_name}"
    )

    service = CogneeService(
        dataset_name=dataset_name
    )

    print(
        "CogneeService created successfully."
    )

    # ------------------------------------------------------
    # STEP 2 — ADD CONTENT
    # ------------------------------------------------------

    print(
        "\n--- STEP 1: ADD CONTENT ---"
    )

    result = await service.add_content(
        TEST_DATA
    )

    print(
        "Content added successfully."
    )

    print(
        "Remember result:"
    )

    print(result)

    # ------------------------------------------------------
    # STEP 3 — SEARCH
    # ------------------------------------------------------

    print(
        "\n--- STEP 2: RECALL ---"
    )

    query = (
        "Explain Bottom-Up Parsing "
        "and Canonical LR parsing tables."
    )

    print(
        f"Query: {query}"
    )

    results = await service.search(
        query=query,
        top_k=5,
        only_context=True,
    )

    print(
        "\n========== RESULTS =========="
    )

    print(
        f"Result count: {len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"\n--- RESULT {index} ---"
        )

        print(result)

    print(
        "\n" + "=" * 65
    )

    print(
        "COGNEE SERVICE TEST COMPLETED"
    )

    print(
        "=" * 65
    )


if __name__ == "__main__":

    asyncio.run(main())