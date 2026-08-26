# scripts/create_confidence_benchmark.py

import json
import random
import re
from pathlib import Path
from collections import defaultdict


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path(
    "uploads/temp/enriched/6thsempyqs_2025"
)

SYLLABUS_INDEX_FILE = Path(
    "uploads/temp/syllabus/syllabus_index.json"
)

OUTPUT_FILE = Path(
    "uploads/temp/m6/confidence_benchmark_50.json"
)

TARGET_SIZE = 50

RANDOM_SEED = 42


# ============================================================
# COURSE CODE NORMALIZATION
# ============================================================

def normalize_course_code(
    course_code: str,
) -> str:
    """
    Normalize course codes so equivalent representations
    are treated as the same course.

    Examples:

        HMC-306  -> HMC 306
        HMC_306  -> HMC 306
        HMC 306  -> HMC 306

    The normalization is applied only to the benchmark
    representation. Original enriched files are untouched.
    """

    if course_code is None:
        return ""

    code = str(
        course_code
    ).strip().upper()

    # Replace hyphens and underscores with spaces
    code = re.sub(
        r"[-_]+",
        " ",
        code,
    )

    # Collapse repeated whitespace
    code = re.sub(
        r"\s+",
        " ",
        code,
    )

    return code


# ============================================================
# LOAD SYLLABUS INDEX
# ============================================================

def load_syllabus_index():
    """
    Load the existing validated syllabus index.

    This is used later to validate that ground-truth
    index_ids belong to the actual structured syllabus.
    """

    if not SYLLABUS_INDEX_FILE.exists():

        raise FileNotFoundError(
            "Syllabus index not found:\n"
            f"{SYLLABUS_INDEX_FILE}"
        )

    records = json.loads(
        SYLLABUS_INDEX_FILE.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        records,
        list,
    ):

        raise ValueError(
            "Syllabus index must contain "
            "a JSON list."
        )

    if not records:

        raise ValueError(
            "Syllabus index is empty."
        )

    index_ids = set()

    for record in records:

        index_id = record.get(
            "index_id"
        )

        if not index_id:

            raise ValueError(
                "Syllabus record missing index_id."
            )

        index_ids.add(
            index_id
        )

    print(
        f"\n✓ Loaded "
        f"{len(index_ids)} syllabus index IDs."
    )

    return index_ids


# ============================================================
# LOAD QUESTIONS
# ============================================================

def load_questions():
    """
    Load all enriched question records from the existing
    M4 enriched-question files.
    """

    if not INPUT_DIR.exists():

        raise FileNotFoundError(
            "Enriched directory not found:\n"
            f"{INPUT_DIR}"
        )

    files = sorted(
        INPUT_DIR.glob(
            "*_questions.json"
        )
    )

    if not files:

        raise FileNotFoundError(
            "No enriched question files found in:\n"
            f"{INPUT_DIR}"
        )

    print(
        f"\nFound {len(files)} enriched paper files."
    )

    all_questions = []

    for file_path in files:

        print(
            f"Loading: {file_path.name}"
        )

        records = json.loads(
            file_path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(
            records,
            list,
        ):

            raise ValueError(
                f"Expected a list in:\n"
                f"{file_path}"
            )

        for record in records:

            # ------------------------------------------------
            # Preserve original data
            # ------------------------------------------------

            question = {
                **record,
                "source_file": (
                    file_path.name
                ),
            }

            # ------------------------------------------------
            # Add normalized course code
            #
            # This does NOT modify the original field.
            # ------------------------------------------------

            question[
                "normalized_course_code"
            ] = normalize_course_code(
                record.get(
                    "subject_code",
                    "",
                )
            )

            all_questions.append(
                question
            )

    return all_questions


# ============================================================
# VALIDATION
# ============================================================

def validate_questions(
    questions,
):
    """
    Validate the minimum fields required for
    benchmark construction.
    """

    required_fields = {
        "paper_id",
        "subject",
        "subject_code",
        "exam_type",
        "semester",
        "question_number",
        "text",
        "unit",
    }

    valid_questions = []

    skipped = 0

    for question in questions:

        missing = (
            required_fields
            - question.keys()
        )

        if missing:

            print(
                "\nWARNING: Skipping record."
            )

            print(
                f"Paper: "
                f"{question.get('paper_id')}"
            )

            print(
                f"Missing: "
                f"{sorted(missing)}"
            )

            skipped += 1

            continue

        text = str(
            question.get(
                "text",
                "",
            )
        ).strip()

        if not text:

            print(
                "\nWARNING: Skipping empty question:"
                f" {question.get('paper_id')}"
            )

            skipped += 1

            continue

        normalized_code = question.get(
            "normalized_course_code",
            "",
        )

        if not normalized_code:

            print(
                "\nWARNING: Skipping question "
                "with empty course code:"
                f" {question.get('paper_id')}"
            )

            skipped += 1

            continue

        valid_questions.append(
            question
        )

    print(
        f"\n✓ Valid questions : "
        f"{len(valid_questions)}"
    )

    print(
        f"✓ Skipped records : "
        f"{skipped}"
    )

    return valid_questions


# ============================================================
# STRATIFICATION
# ============================================================

def build_groups(
    questions,
):
    """
    Create strata using:

        normalized course code
        exam type
        unit

    This ensures equivalent course-code representations
    such as HMC-306 and HMC 306 belong to the same strata.
    """

    groups = defaultdict(list)

    for question in questions:

        key = (
            question[
                "normalized_course_code"
            ],
            question["exam_type"],
            int(question["unit"]),
        )

        groups[key].append(
            question
        )

    return groups


# ============================================================
# STRATIFIED SAMPLING
# ============================================================

def select_benchmark(
    questions,
    target_size,
):
    """
    Select a representative benchmark using
    stratified sampling.

    Primary strata:

        normalized course code
        exam type
        unit

    A deterministic random seed is used so the
    benchmark can be reproduced.
    """

    random.seed(
        RANDOM_SEED
    )

    groups = build_groups(
        questions
    )

    print(
        f"\nNumber of strata: "
        f"{len(groups)}"
    )

    # --------------------------------------------------------
    # Shuffle every group deterministically
    # --------------------------------------------------------

    for group in groups.values():

        random.shuffle(
            group
        )

    # --------------------------------------------------------
    # First pass:
    # Give each available group one question.
    # --------------------------------------------------------

    selected = []

    remaining = []

    for key, group in groups.items():

        if group:

            selected.append(
                group.pop()
            )

            remaining.extend(
                group
            )

    # --------------------------------------------------------
    # If number of strata exceeds target size,
    # randomly trim.
    # --------------------------------------------------------

    if len(selected) > target_size:

        random.shuffle(
            selected
        )

        selected = selected[
            :target_size
        ]

        return selected

    # --------------------------------------------------------
    # Second pass:
    # Fill remaining slots.
    # --------------------------------------------------------

    random.shuffle(
        remaining
    )

    slots_left = (
        target_size
        - len(selected)
    )

    selected.extend(
        remaining[
            :slots_left
        ]
    )

    return selected


# ============================================================
# REMOVE DUPLICATE QUESTION TEXT
# ============================================================

def remove_duplicates(
    questions,
):
    """
    Remove exact duplicate question text while preserving
    the first occurrence.

    This prevents the benchmark from wasting slots on
    identical questions appearing multiple times.
    """

    seen = set()

    unique = []

    for question in questions:

        text = (
            question["text"]
            .strip()
            .lower()
        )

        if text in seen:

            continue

        seen.add(
            text
        )

        unique.append(
            question
        )

    return unique


# ============================================================
# CONVERT TO BENCHMARK FORMAT
# ============================================================

def create_benchmark_records(
    questions,
):
    """
    Convert enriched questions into the benchmark format.

    Ground-truth fields are intentionally left empty.

    They must be manually verified against the structured
    syllabus.
    """

    benchmark = []

    for index, question in enumerate(
        questions,
        start=1,
    ):

        normalized_course_code = (
            question[
                "normalized_course_code"
            ]
        )

        benchmark_record = {

            # ------------------------------------------------
            # Benchmark identity
            # ------------------------------------------------

            "benchmark_id": (
                f"M66_{index:03d}"
            ),

            # ------------------------------------------------
            # Original question identity
            # ------------------------------------------------

            "paper_id": question[
                "paper_id"
            ],

            "source_file": question[
                "source_file"
            ],

            "subject": question[
                "subject"
            ],

            # Keep original code too
            "original_subject_code": (
                question[
                    "subject_code"
                ]
            ),

            # Use normalized code for M6 evaluation
            "subject_code": (
                normalized_course_code
            ),

            "exam_type": question[
                "exam_type"
            ],

            "semester": question[
                "semester"
            ],

            "question_number": question[
                "question_number"
            ],

            "sub_question": question.get(
                "sub_question"
            ),

            "text": question[
                "text"
            ],

            # ------------------------------------------------
            # Existing M4 unit metadata
            # ------------------------------------------------

            "m4_unit": question[
                "unit"
            ],

            # ------------------------------------------------
            # Ground truth
            #
            # THESE MUST BE MANUALLY VERIFIED.
            # ------------------------------------------------

            "ground_truth": {

                # Exact syllabus record
                "index_id": None,

                "unit": None,

                "topic": None,

                "subtopic": None,
            },

            # ------------------------------------------------
            # M6 prediction fields
            # ------------------------------------------------

            "prediction": {

                "index_id": None,

                "unit": None,

                "topic": None,

                "subtopic": None,
            },

            # ------------------------------------------------
            # Evaluation fields
            # ------------------------------------------------

            "evaluation": {

                "unit_correct": None,

                "topic_correct": None,

                "subtopic_correct": None,
            },
        }

        benchmark.append(
            benchmark_record
        )

    return benchmark


# ============================================================
# STATISTICS
# ============================================================

def print_statistics(
    benchmark,
):
    print(
        "\n" + "=" * 80
    )

    print(
        "BENCHMARK STATISTICS"
    )

    print(
        "=" * 80
    )

    print(
        f"\nTotal benchmark questions: "
        f"{len(benchmark)}"
    )

    # --------------------------------------------------------
    # Subject distribution
    # --------------------------------------------------------

    subjects = defaultdict(int)

    for record in benchmark:

        subjects[
            record["subject_code"]
        ] += 1

    print(
        "\nSubject distribution:"
    )

    for subject, count in sorted(
        subjects.items()
    ):

        print(
            f"  {subject:<12} : "
            f"{count}"
        )

    # --------------------------------------------------------
    # Original subject-code distribution
    # --------------------------------------------------------

    original_subjects = defaultdict(int)

    for record in benchmark:

        original_subjects[
            record["original_subject_code"]
        ] += 1

    print(
        "\nOriginal subject-code distribution:"
    )

    for subject, count in sorted(
        original_subjects.items()
    ):

        print(
            f"  {subject:<12} : "
            f"{count}"
        )

    # --------------------------------------------------------
    # Exam distribution
    # --------------------------------------------------------

    exams = defaultdict(int)

    for record in benchmark:

        exams[
            record["exam_type"]
        ] += 1

    print(
        "\nExam type distribution:"
    )

    for exam_type, count in sorted(
        exams.items()
    ):

        print(
            f"  {exam_type:<12} : "
            f"{count}"
        )

    # --------------------------------------------------------
    # Unit distribution
    # --------------------------------------------------------

    units = defaultdict(int)

    for record in benchmark:

        key = (
            record["subject_code"],
            record["m4_unit"],
        )

        units[key] += 1

    print(
        "\nSubject + Unit distribution:"
    )

    for (
        subject_code,
        unit,
    ), count in sorted(
        units.items()
    ):

        print(
            f"  {subject_code} "
            f"Unit {unit}: "
            f"{count}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 80
    )

    print(
        "M6.6.2 - CONFIDENCE BENCHMARK CREATION"
    )

    print(
        "=" * 80
    )

    print(
        f"\nInput directory:"
        f"\n{INPUT_DIR}"
    )

    print(
        f"\nSyllabus index:"
        f"\n{SYLLABUS_INDEX_FILE}"
    )

    print(
        f"\nTarget benchmark size:"
        f" {TARGET_SIZE}"
    )

    print(
        f"Random seed:"
        f" {RANDOM_SEED}"
    )

    # --------------------------------------------------------
    # 1. Load syllabus index
    # --------------------------------------------------------

    syllabus_index_ids = (
        load_syllabus_index()
    )

    # --------------------------------------------------------
    # 2. Load questions
    # --------------------------------------------------------

    questions = load_questions()

    print(
        f"\n✓ Loaded "
        f"{len(questions)} total records."
    )

    # --------------------------------------------------------
    # 3. Validate questions
    # --------------------------------------------------------

    questions = validate_questions(
        questions
    )

    # --------------------------------------------------------
    # 4. Remove exact duplicates
    # --------------------------------------------------------

    before = len(
        questions
    )

    questions = remove_duplicates(
        questions
    )

    after = len(
        questions
    )

    print(
        f"\n✓ Removed "
        f"{before - after} exact duplicates."
    )

    print(
        f"✓ Unique questions: "
        f"{after}"
    )

    if len(questions) < TARGET_SIZE:

        raise ValueError(
            f"Only {len(questions)} unique "
            f"questions available, but "
            f"{TARGET_SIZE} are required."
        )

    # --------------------------------------------------------
    # 5. Select benchmark
    # --------------------------------------------------------

    benchmark_questions = (
        select_benchmark(
            questions,
            TARGET_SIZE,
        )
    )

    # --------------------------------------------------------
    # 6. Sort benchmark for readability
    # --------------------------------------------------------

    benchmark_questions.sort(
        key=lambda q: (
            q[
                "normalized_course_code"
            ],
            q["exam_type"],
            int(q["unit"]),
            str(q["question_number"]),
        )
    )

    # --------------------------------------------------------
    # 7. Create benchmark records
    # --------------------------------------------------------

    benchmark = (
        create_benchmark_records(
            benchmark_questions
        )
    )

    # --------------------------------------------------------
    # 8. Verify benchmark ground-truth
    # --------------------------------------------------------

    #
    # Ground-truth index IDs are intentionally None here,
    # so this validation simply verifies that the syllabus
    # index was successfully loaded and available for the
    # manual-labeling stage.
    #

    if not syllabus_index_ids:

        raise RuntimeError(
            "No syllabus index IDs available."
        )

    # --------------------------------------------------------
    # 9. Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            benchmark,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 10. Statistics
    # --------------------------------------------------------

    print_statistics(
        benchmark
    )

    # --------------------------------------------------------
    # 11. Completion
    # --------------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "M6.6.2 BENCHMARK CREATION COMPLETED"
    )

    print(
        "=" * 80
    )

    print(
        f"\nBenchmark records:"
        f" {len(benchmark)}"
    )

    print(
        f"\nOutput:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "Course codes have been normalized "
        "for benchmark grouping."
    )

    print(
        "Original course codes are preserved "
        "in original_subject_code."
    )

    print(
        "\nGround-truth fields are still empty."
    )

    print(
        "For each benchmark question, manually "
        "select the exact syllabus index_id "
        "from syllabus_index.json and fill:"
    )

    print(
        "\n"
        "ground_truth.index_id\n"
        "ground_truth.unit\n"
        "ground_truth.topic\n"
        "ground_truth.subtopic"
    )

    print(
        "\n" + "=" * 80
    )


if __name__ == "__main__":
    main()