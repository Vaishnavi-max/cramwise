# scripts/label_confidence_benchmark.py

import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BENCHMARK_FILE = Path(
    "uploads/temp/m6/confidence_benchmark_50.json"
)

SYLLABUS_FILE = Path(
    "uploads/temp/syllabus/syllabus_index.json"
)


# ============================================================
# COURSE CODE NORMALIZATION
# ============================================================

def normalize_course_code(course_code):
    """
    Normalize course codes so that variants such as:

        HMC-306
        HMC 306

    are treated as the same course.
    """

    if course_code is None:
        return ""

    return (
        str(course_code)
        .strip()
        .upper()
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"File not found:\n{path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# SAVE JSON
# ============================================================

def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# DISPLAY QUESTION
# ============================================================

def display_question(record, current, total):

    print("\n")
    print("=" * 80)
    print(
        f"QUESTION {current}/{total}"
    )
    print("=" * 80)

    print(
        f"Benchmark ID : {record.get('benchmark_id')}"
    )

    print(
        f"Course       : {record.get('subject')}"
    )

    print(
        f"Course Code  : {record.get('subject_code')}"
    )

    print(
        f"Exam Type    : {record.get('exam_type')}"
    )

    print(
        f"Question No. : {record.get('question_number')}"
    )

    if record.get("sub_question"):
        print(
            f"Sub-question: {record.get('sub_question')}"
        )

    print(
        f"M4 Unit Hint : {record.get('m4_unit')}"
    )

    print("\nQuestion:")
    print("-" * 80)
    print(
        record.get("text", "").strip()
    )
    print("-" * 80)


# ============================================================
# FIND SYLLABUS CANDIDATES
# ============================================================

def find_candidates(
    benchmark_record,
    syllabus_records,
):
    """
    Narrow the syllabus using:

        1. course code
        2. unit

    The actual final ground truth is selected manually
    from these candidates.
    """

    benchmark_course = normalize_course_code(
        benchmark_record.get(
            "subject_code"
        )
    )

    benchmark_unit = benchmark_record.get(
        "m4_unit"
    )

    candidates = []

    for record in syllabus_records:

        syllabus_course = normalize_course_code(
            record.get("course_code")
        )

        if syllabus_course != benchmark_course:
            continue

        try:
            syllabus_unit = int(
                record.get("unit_number")
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        if benchmark_unit is not None:

            try:
                if syllabus_unit != int(
                    benchmark_unit
                ):
                    continue
            except (
                TypeError,
                ValueError,
            ):
                continue

        candidates.append(record)

    return candidates


# ============================================================
# DISPLAY CANDIDATES
# ============================================================

def display_candidates(candidates):

    print("\n")
    print("=" * 80)
    print("SYLLABUS CANDIDATES")
    print("=" * 80)

    if not candidates:

        print(
            "\n⚠ No candidates found using "
            "course + unit filtering."
        )

        return

    for i, record in enumerate(
        candidates,
        start=1,
    ):

        print("\n")
        print(
            f"[{i}] {record.get('index_id')}"
        )

        print(
            f"    Course   : "
            f"{record.get('course_name')}"
        )

        print(
            f"    Unit     : "
            f"{record.get('unit_number')}"
        )

        print(
            f"    Topic    : "
            f"{record.get('topic')}"
        )

        print(
            f"    Subtopic : "
            f"{record.get('subtopic')}"
        )

        print(
            f"    Search   : "
            f"{record.get('search_text')}"
        )

    print("\n" + "-" * 80)


# ============================================================
# SELECT CANDIDATE
# ============================================================

def select_candidate(
    candidates,
):

    while True:

        choice = input(
            "\nSelect correct candidate "
            "(number / s=skip / q=quit): "
        ).strip().lower()

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if choice == "q":
            return "QUIT"

        # ----------------------------------------------------
        # SKIP
        # ----------------------------------------------------

        if choice == "s":
            return None

        # ----------------------------------------------------
        # NUMBER
        # ----------------------------------------------------

        try:
            number = int(choice)
        except ValueError:

            print(
                "❌ Enter a valid number, "
                "'s', or 'q'."
            )

            continue

        if number < 1 or number > len(
            candidates
        ):

            print(
                f"❌ Choose a number "
                f"between 1 and {len(candidates)}."
            )

            continue

        return candidates[
            number - 1
        ]


# ============================================================
# APPLY GROUND TRUTH
# ============================================================

def apply_ground_truth(
    benchmark_record,
    syllabus_record,
):
    """
    Copy the authoritative syllabus metadata
    into the benchmark ground_truth field.
    """

    benchmark_record[
        "ground_truth"
    ] = {
        "index_id": syllabus_record.get(
            "index_id"
        ),
        "unit": syllabus_record.get(
            "unit_number"
        ),
        "topic": syllabus_record.get(
            "topic"
        ),
        "subtopic": syllabus_record.get(
            "subtopic"
        ),
    }


# ============================================================
# PROGRESS
# ============================================================

def count_labeled(records):

    count = 0

    for record in records:

        ground_truth = record.get(
            "ground_truth",
            {}
        )

        if ground_truth.get(
            "index_id"
        ):

            count += 1

    return count


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("M6.6.2 - CONFIDENCE BENCHMARK GROUND-TRUTH LABELING")
    print("=" * 80)

    # --------------------------------------------------------
    # 1. LOAD BENCHMARK
    # --------------------------------------------------------

    print(
        f"\nBenchmark:"
        f"\n{BENCHMARK_FILE}"
    )

    benchmark_records = load_json(
        BENCHMARK_FILE
    )

    print(
        f"✓ Loaded "
        f"{len(benchmark_records)} benchmark records."
    )

    # --------------------------------------------------------
    # 2. LOAD SYLLABUS
    # --------------------------------------------------------

    print(
        f"\nSyllabus index:"
        f"\n{SYLLABUS_FILE}"
    )

    syllabus_records = load_json(
        SYLLABUS_FILE
    )

    print(
        f"✓ Loaded "
        f"{len(syllabus_records)} syllabus records."
    )

    # --------------------------------------------------------
    # 3. INITIAL PROGRESS
    # --------------------------------------------------------

    labeled = count_labeled(
        benchmark_records
    )

    print(
        f"\nAlready labeled : {labeled}"
    )

    print(
        f"Remaining       : "
        f"{len(benchmark_records) - labeled}"
    )

    print("\n")
    print("=" * 80)
    print("LABELING INSTRUCTIONS")
    print("=" * 80)

    print(
        """
For each question:

1. Read the question carefully.
2. Look at the syllabus candidates.
3. Select the EXACT syllabus entry that best represents
   what the question is asking.
4. The selected entry's index_id, unit, topic and subtopic
   will be stored automatically.

Commands:
    number -> select candidate
    s      -> skip question
    q      -> save and quit

Progress is saved after EVERY labeled question.
"""
    )

    input(
        "\nPress ENTER to start..."
    )

    # --------------------------------------------------------
    # 4. PROCESS QUESTIONS
    # --------------------------------------------------------

    total = len(
        benchmark_records
    )

    for i, benchmark_record in enumerate(
        benchmark_records,
        start=1,
    ):

        # ----------------------------------------------------
        # Skip already labeled questions
        # ----------------------------------------------------

        existing_ground_truth = (
            benchmark_record.get(
                "ground_truth",
                {}
            )
        )

        if existing_ground_truth.get(
            "index_id"
        ):

            continue

        # ----------------------------------------------------
        # Display question
        # ----------------------------------------------------

        display_question(
            benchmark_record,
            i,
            total,
        )

        # ----------------------------------------------------
        # Find candidates
        # ----------------------------------------------------

        candidates = find_candidates(
            benchmark_record,
            syllabus_records,
        )

        display_candidates(
            candidates
        )

        # ----------------------------------------------------
        # No candidates
        # ----------------------------------------------------

        if not candidates:

            print(
                "\n⚠ No syllabus candidates "
                "were found."
            )

            print(
                "Skipping this question."
            )

            continue

        # ----------------------------------------------------
        # Select candidate
        # ----------------------------------------------------

        selected = select_candidate(
            candidates
        )

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        if selected == "QUIT":

            save_json(
                BENCHMARK_FILE,
                benchmark_records,
            )

            print(
                "\n✓ Progress saved."
            )

            print(
                f"Labeled questions: "
                f"{count_labeled(benchmark_records)}"
            )

            print(
                "\nExiting labeling tool."
            )

            return

        # ----------------------------------------------------
        # Skip
        # ----------------------------------------------------

        if selected is None:

            print(
                "\n⏭ Question skipped."
            )

            continue

        # ----------------------------------------------------
        # Apply ground truth
        # ----------------------------------------------------

        apply_ground_truth(
            benchmark_record,
            selected,
        )

        # ----------------------------------------------------
        # SAVE IMMEDIATELY
        # ----------------------------------------------------

        save_json(
            BENCHMARK_FILE,
            benchmark_records,
        )

        print("\n")
        print("=" * 80)
        print("✓ GROUND TRUTH SAVED")
        print("=" * 80)

        print(
            f"Index ID : "
            f"{selected.get('index_id')}"
        )

        print(
            f"Unit     : "
            f"{selected.get('unit_number')}"
        )

        print(
            f"Topic    : "
            f"{selected.get('topic')}"
        )

        print(
            f"Subtopic : "
            f"{selected.get('subtopic')}"
        )

        print(
            f"\nProgress: "
            f"{count_labeled(benchmark_records)}"
            f"/{total}"
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("M6.6.2 GROUND-TRUTH LABELING COMPLETED")
    print("=" * 80)

    print(
        f"\nTotal questions : {total}"
    )

    print(
        f"Labeled         : "
        f"{count_labeled(benchmark_records)}"
    )

    print(
        f"Remaining       : "
        f"{total - count_labeled(benchmark_records)}"
    )

    print(
        f"\nUpdated benchmark:"
        f"\n{BENCHMARK_FILE}"
    )

    print("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()