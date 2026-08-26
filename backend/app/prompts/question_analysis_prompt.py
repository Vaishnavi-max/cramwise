"""
Prompt used by the Question Analysis Layer.

M4 uses this prompt to:
1. Identify the syllabus topic/subtopic tested by a PYQ.
2. Determine whether the topic has important prerequisites.

The prompt is intentionally kept separate from the service
so that LLM instructions can be improved independently.
"""


# ==========================================================
# SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are the academic analysis engine for CramWise.

Your task is to analyze ONE university previous-year question
and map it to the provided syllabus.

You must perform two tasks:

1. Identify the best matching syllabus topic/subtopic.
2. Determine whether understanding another syllabus topic
   is important before studying the selected topic.


IMPORTANT RULES:

- Select the syllabus record that best represents the MAIN
  concept being tested by the question.

- Use ONLY the syllabus records provided in the prompt.

- NEVER invent a syllabus topic.

- NEVER create, modify, shorten, extend, or reconstruct
  an index_id.

- topic_id MUST be copied EXACTLY from one of the provided
  index_id values.

- If a syllabus record has an index_id such as:

      HMC306_U1_T03

  you MUST return exactly:

      HMC306_U1_T03

  Do NOT create:

      HMC306_U1_T03_S01
      HMC306_U1_T03_S02

  unless those exact IDs are explicitly present in the
  provided syllabus candidates.

- The topic and subtopic must correspond exactly to the
  selected topic_id.

- A question may mention multiple concepts. Select the MAIN
  concept being tested.

- Mark is_independent = false only when another provided
  syllabus topic is genuinely important as a prerequisite.

- prerequisites MUST contain ONLY exact index_id values copied
  from the provided syllabus candidates.

- If there is no meaningful prerequisite, return an empty list.

- Keep evidence short and factual.

- Do not provide chain-of-thought reasoning.

- Return only the requested structured output.
"""


# ==========================================================
# USER PROMPT BUILDER
# ==========================================================

def build_user_prompt(
    question: dict,
    unit_candidates: list[dict],
) -> str:
    """
    Build the user prompt sent to the LLM.

    The prompt contains:

        1. The PYQ
        2. Syllabus candidates from the same subject/unit

    We intentionally do NOT send the complete syllabus.

    This keeps the request compact and gives the LLM only
    the syllabus context that is relevant to the question.
    """

    # ------------------------------------------------------
    # QUESTION SECTION
    # ------------------------------------------------------

    question_section = f"""
QUESTION

Subject: {question.get("subject")}
Subject Code: {question.get("subject_code")}
Unit: {question.get("unit")}
Question Number: {question.get("question_number")}
Marks: {question.get("marks")}

Question Text:
{question.get("text")}
"""


    # ------------------------------------------------------
    # SYLLABUS CANDIDATES SECTION
    # ------------------------------------------------------

    candidates_section = """
SYLLABUS CANDIDATES

These are the syllabus records belonging to the same
subject and unit as the question.

IMPORTANT:
You MUST copy index_id EXACTLY as provided below.

Do NOT construct a new index_id.
Do NOT add an S01/S02/S03 suffix unless it is explicitly
present in the candidate list.

"""

    for record in unit_candidates:

        candidates_section += (
            f"- index_id: {record['index_id']}\n"
            f"  topic: {record['topic']}\n"
            f"  subtopic: {record['subtopic']}\n"
        )


    # ------------------------------------------------------
    # FINAL PROMPT
    # ------------------------------------------------------

    return (
        question_section
        + "\n"
        + candidates_section
    )