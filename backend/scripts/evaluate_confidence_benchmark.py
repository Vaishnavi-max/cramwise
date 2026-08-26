# scripts/evaluate_confidence_benchmark.py

import json
import time
from pathlib import Path

from app.services.hybrid_retrieval_service import (
    HybridRetrievalService,
)

from app.services.cross_encoder_service import (
    CrossEncoderService,
)


# ============================================================
# PATHS
# ============================================================

BENCHMARK_FILE = Path(
    "uploads/temp/m6/confidence_benchmark_50.json"
)

OUTPUT_FILE = Path(
    "uploads/temp/m6/confidence_evaluation_43.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

HYBRID_TOP_K = 10
RERANK_TOP_K = 10


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(path: Path):
    """
    Load JSON file.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"File not found:\n{path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def save_json(
    path: Path,
    data,
):
    """
    Save JSON file.
    """

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
# VALUE NORMALIZATION
# ============================================================

def normalize_optional_string(value):
    """
    Normalize optional string values.

    These values all represent
    'no value':

        None
        ""
        "None"
        "null"

    They are converted to:

        None

    Real values are preserved.
    """

    if value is None:

        return None

    if isinstance(value, str):

        value = value.strip()

        if not value:

            return None

        if value.lower() in {
            "none",
            "null",
        }:

            return None

    return value


def normalize_subtopic(value):
    """
    Normalize syllabus subtopic values.

    This is kept as a separate function so
    subtopic comparison is explicit.
    """

    return normalize_optional_string(
        value
    )


# ============================================================
# GROUND-TRUTH VALIDATION
# ============================================================

def validate_ground_truth(records):
    """
    Separate labeled and unlabeled benchmark
    questions.

    A question is considered labeled when:

        ground_truth.index_id

    exists.

    Unlabeled questions are skipped.

    IMPORTANT:

    Missing ground truth does NOT mean
    the system prediction is incorrect.
    """

    labeled = []

    unlabeled = []

    for record in records:

        ground_truth = record.get(
            "ground_truth"
        )

        if (
            ground_truth
            and ground_truth.get(
                "index_id"
            )
        ):

            labeled.append(
                record
            )

        else:

            unlabeled.append(
                record.get(
                    "benchmark_id"
                )
            )

    print(
        f"\n✓ Labeled questions   : "
        f"{len(labeled)}"
    )

    print(
        f"✓ Unlabeled questions : "
        f"{len(unlabeled)}"
    )

    if unlabeled:

        print(
            "\n⚠ These questions will be "
            "SKIPPED during evaluation:"
        )

        for benchmark_id in unlabeled:

            print(
                f"  - {benchmark_id}"
            )

    return labeled, unlabeled


# ============================================================
# BUILD PREDICTION
# ============================================================

def build_prediction(
    top_candidate,
):
    """
    Convert the top reranked syllabus
    candidate into the final prediction.
    """

    return {

        "index_id": top_candidate.get(
            "index_id"
        ),

        "unit": top_candidate.get(
            "unit_number"
        ),

        "topic": top_candidate.get(
            "topic"
        ),

        "subtopic": top_candidate.get(
            "subtopic"
        ),
    }


# ============================================================
# EVALUATE PREDICTION
# ============================================================

def evaluate_prediction(
    ground_truth,
    prediction,
    reranked_results,
):
    """
    Compare predicted syllabus mapping
    against manually labeled ground truth.

    Evaluation levels:

        index
        unit
        topic
        subtopic

    Also calculates:

        ground-truth rank
        Recall@1
        Recall@3
        Recall@5
        Recall@10
        Reciprocal Rank
    """

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    ground_truth_id = (
        ground_truth.get(
            "index_id"
        )
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predicted_id = (
        prediction.get(
            "index_id"
        )
    )

    # --------------------------------------------------------
    # Exact index correctness
    # --------------------------------------------------------

    index_correct = (
        predicted_id
        == ground_truth_id
    )

    # --------------------------------------------------------
    # Unit correctness
    # --------------------------------------------------------

    predicted_unit = (
        prediction.get(
            "unit"
        )
    )

    actual_unit = (
        ground_truth.get(
            "unit"
        )
    )

    unit_correct = (
        predicted_unit
        == actual_unit
    )

    # --------------------------------------------------------
    # Topic correctness
    # --------------------------------------------------------

    predicted_topic = (
        normalize_optional_string(
            prediction.get(
                "topic"
            )
        )
    )

    actual_topic = (
        normalize_optional_string(
            ground_truth.get(
                "topic"
            )
        )
    )

    topic_correct = (
        predicted_topic
        == actual_topic
    )

    # --------------------------------------------------------
    # Subtopic correctness
    #
    # IMPORTANT:
    #
    # None
    # ""
    # "None"
    # "null"
    #
    # are treated as the same value.
    # --------------------------------------------------------

    predicted_subtopic = (
        normalize_subtopic(
            prediction.get(
                "subtopic"
            )
        )
    )

    actual_subtopic = (
        normalize_subtopic(
            ground_truth.get(
                "subtopic"
            )
        )
    )

    subtopic_correct = (
        predicted_subtopic
        == actual_subtopic
    )

    # --------------------------------------------------------
    # Find ground-truth rank
    # --------------------------------------------------------

    ground_truth_rank = None

    for rank, candidate in enumerate(
        reranked_results,
        start=1,
    ):

        if (
            candidate.get(
                "index_id"
            )
            == ground_truth_id
        ):

            ground_truth_rank = rank

            break

    # --------------------------------------------------------
    # Recall@K
    # --------------------------------------------------------

    top1_correct = (
        ground_truth_rank == 1
    )

    top3_contains_correct = (
        ground_truth_rank is not None
        and ground_truth_rank <= 3
    )

    top5_contains_correct = (
        ground_truth_rank is not None
        and ground_truth_rank <= 5
    )

    top10_contains_correct = (
        ground_truth_rank is not None
        and ground_truth_rank <= 10
    )

    # --------------------------------------------------------
    # Reciprocal Rank
    #
    # rank 1 -> 1
    # rank 2 -> 0.5
    # rank 3 -> 0.333...
    #
    # not found -> 0
    # --------------------------------------------------------

    if ground_truth_rank is not None:

        reciprocal_rank = (
            1.0 / ground_truth_rank
        )

    else:

        reciprocal_rank = 0.0

    return {

        "index_correct": (
            index_correct
        ),

        "unit_correct": (
            unit_correct
        ),

        "topic_correct": (
            topic_correct
        ),

        "subtopic_correct": (
            subtopic_correct
        ),

        "ground_truth_rank": (
            ground_truth_rank
        ),

        "top1_correct": (
            top1_correct
        ),

        "top3_contains_correct": (
            top3_contains_correct
        ),

        "top5_contains_correct": (
            top5_contains_correct
        ),

        "top10_contains_correct": (
            top10_contains_correct
        ),

        "reciprocal_rank": (
            reciprocal_rank
        ),
    }


# ============================================================
# CONFIDENCE SIGNAL EXTRACTION
# ============================================================

def extract_confidence_signals(
    reranked_results,
):
    """
    Extract M6.6.1 confidence signals.

    No HIGH / MEDIUM / LOW decision
    is made here.

    That will happen in M6.6.4.
    """

    if not reranked_results:

        raise ValueError(
            "No reranked candidates returned."
        )

    # --------------------------------------------------------
    # Top scores
    # --------------------------------------------------------

    top1 = float(
        reranked_results[0].get(
            "reranker_score",
            0.0,
        )
    )

    if len(reranked_results) >= 2:

        top2 = float(
            reranked_results[1].get(
                "reranker_score",
                0.0,
            )
        )

    else:

        top2 = 0.0

    if len(reranked_results) >= 3:

        top3 = float(
            reranked_results[2].get(
                "reranker_score",
                0.0,
            )
        )

    else:

        top3 = 0.0

    # --------------------------------------------------------
    # Score gaps
    # --------------------------------------------------------

    top1_top2_gap = (
        top1 - top2
    )

    top1_top3_gap = (
        top1 - top3
    )

    # --------------------------------------------------------
    # Top1 / Top2 ratio
    # --------------------------------------------------------

    if abs(top2) > 1e-12:

        top1_top2_ratio = (
            top1 / top2
        )

    else:

        top1_top2_ratio = None

    # --------------------------------------------------------
    # Score distribution
    # --------------------------------------------------------

    scores = []

    for candidate in reranked_results:

        scores.append(
            float(
                candidate.get(
                    "reranker_score",
                    0.0,
                )
            )
        )

    score_min = min(
        scores
    )

    score_max = max(
        scores
    )

    score_mean = (
        sum(scores)
        / len(scores)
    )

    # --------------------------------------------------------
    # Top candidate retrieval information
    # --------------------------------------------------------

    top_candidate = (
        reranked_results[0]
    )

    bge_rank = (
        top_candidate.get(
            "bge_rank"
        )
    )

    bm25_rank = (
        top_candidate.get(
            "bm25_rank"
        )
    )

    hybrid_rank = (
        top_candidate.get(
            "hybrid_rank"
        )
    )

    reranker_rank = (
        top_candidate.get(
            "reranker_rank"
        )
    )

    # --------------------------------------------------------
    # BGE / BM25 agreement
    #
    # Here "agreement" means the top candidate
    # appeared at the same rank in both systems.
    # --------------------------------------------------------

    bge_bm25_agree = (

        bge_rank is not None

        and

        bm25_rank is not None

        and

        bge_rank == bm25_rank
    )

    # --------------------------------------------------------
    # Retrieved by both systems
    # --------------------------------------------------------

    retrieved_by_both = (

        bge_rank is not None

        and

        bm25_rank is not None
    )

    return {

        "top1_score": (
            top1
        ),

        "top2_score": (
            top2
        ),

        "top3_score": (
            top3
        ),

        "top1_top2_gap": (
            top1_top2_gap
        ),

        "top1_top2_ratio": (
            top1_top2_ratio
        ),

        "top1_top3_gap": (
            top1_top3_gap
        ),

        "reranker_rank": (
            reranker_rank
        ),

        "hybrid_rank": (
            hybrid_rank
        ),

        "bge_rank": (
            bge_rank
        ),

        "bm25_rank": (
            bm25_rank
        ),

        "bge_bm25_agree": (
            bge_bm25_agree
        ),

        "retrieved_by_both": (
            retrieved_by_both
        ),

        "score_min": (
            score_min
        ),

        "score_max": (
            score_max
        ),

        "score_mean": (
            score_mean
        ),

        "candidate_count": (
            len(reranked_results)
        ),
    }


# ============================================================
# CANDIDATE OUTPUT
# ============================================================

def build_candidate_output(
    candidate,
):
    """
    Preserve retrieval and reranking
    information for each candidate.
    """

    return {

        "index_id": candidate.get(
            "index_id"
        ),

        "course_code": candidate.get(
            "course_code"
        ),

        "course_name": candidate.get(
            "course_name"
        ),

        "semester": candidate.get(
            "semester"
        ),

        "unit": candidate.get(
            "unit_number"
        ),

        "topic": candidate.get(
            "topic"
        ),

        "subtopic": candidate.get(
            "subtopic"
        ),

        "search_text": candidate.get(
            "search_text"
        ),

        "reranker_score": candidate.get(
            "reranker_score"
        ),

        "reranker_rank": candidate.get(
            "reranker_rank"
        ),

        "hybrid_rank": candidate.get(
            "hybrid_rank"
        ),

        "rrf_score": candidate.get(
            "rrf_score"
        ),

        "bge_rank": candidate.get(
            "bge_rank"
        ),

        "bm25_rank": candidate.get(
            "bm25_rank"
        ),

        "bge_score": candidate.get(
            "bge_score"
        ),

        "bm25_score": candidate.get(
            "bm25_score"
        ),
    }


# ============================================================
# SUMMARY METRICS
# ============================================================

def calculate_summary(
    results,
):
    """
    Calculate aggregate benchmark metrics.

    The denominator is ONLY the number
    of evaluated labeled questions.
    """

    total = len(
        results
    )

    if total == 0:

        return {}

    # --------------------------------------------------------
    # Exact index accuracy
    # --------------------------------------------------------

    index_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "index_correct"
        ]
    )

    # --------------------------------------------------------
    # Unit accuracy
    # --------------------------------------------------------

    unit_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "unit_correct"
        ]
    )

    # --------------------------------------------------------
    # Topic accuracy
    # --------------------------------------------------------

    topic_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "topic_correct"
        ]
    )

    # --------------------------------------------------------
    # Subtopic accuracy
    # --------------------------------------------------------

    subtopic_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "subtopic_correct"
        ]
    )

    # --------------------------------------------------------
    # Recall@1
    # --------------------------------------------------------

    top1_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "top1_correct"
        ]
    )

    # --------------------------------------------------------
    # Recall@3
    # --------------------------------------------------------

    top3_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "top3_contains_correct"
        ]
    )

    # --------------------------------------------------------
    # Recall@5
    # --------------------------------------------------------

    top5_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "top5_contains_correct"
        ]
    )

    # --------------------------------------------------------
    # Recall@10
    # --------------------------------------------------------

    top10_correct = sum(

        1

        for result in results

        if result[
            "evaluation"
        ][
            "top10_contains_correct"
        ]
    )

    # --------------------------------------------------------
    # MRR
    # --------------------------------------------------------

    mrr = (

        sum(

            result[
                "evaluation"
            ][
                "reciprocal_rank"
            ]

            for result in results

        )

        / total
    )

    return {

        "total_questions_evaluated": (
            total
        ),

        "index_accuracy": (
            index_correct
            / total
        ),

        "unit_accuracy": (
            unit_correct
            / total
        ),

        "topic_accuracy": (
            topic_correct
            / total
        ),

        "subtopic_accuracy": (
            subtopic_correct
            / total
        ),

        "recall_at_1": (
            top1_correct
            / total
        ),

        "recall_at_3": (
            top3_correct
            / total
        ),

        "recall_at_5": (
            top5_correct
            / total
        ),

        "recall_at_10": (
            top10_correct
            / total
        ),

        "mrr": mrr,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)

    print(
        "M6.6.2 - CONFIDENCE BENCHMARK "
        "BATCH EVALUATION"
    )

    print("=" * 80)

    # ========================================================
    # 1. LOAD BENCHMARK
    # ========================================================

    print(
        f"\nBenchmark:"
        f"\n{BENCHMARK_FILE}"
    )

    benchmark_records = load_json(
        BENCHMARK_FILE
    )

    print(
        f"✓ Loaded "
        f"{len(benchmark_records)} "
        f"questions."
    )

    # ========================================================
    # 2. FILTER LABELED QUESTIONS
    # ========================================================

    print(
        "\nValidating ground truth..."
    )

    (
        labeled_records,
        unlabeled_ids,
    ) = validate_ground_truth(
        benchmark_records
    )

    if not labeled_records:

        raise ValueError(
            "No labeled benchmark "
            "questions available."
        )

    print(
        f"\n✓ Evaluating "
        f"{len(labeled_records)} "
        f"labeled questions."
    )

    # ========================================================
    # 3. INITIALIZE HYBRID RETRIEVAL
    # ========================================================

    print(
        "\nInitializing hybrid retrieval..."
    )

    hybrid = (
        HybridRetrievalService(
            bge_top_k=10,
            bm25_top_k=10,
            rrf_k=60,
        )
    )

    print(
        "✓ Hybrid retrieval initialized."
    )

    # ========================================================
    # 4. INITIALIZE CROSS ENCODER
    # ========================================================

    print(
        "\nInitializing cross-encoder..."
    )

    reranker = (
        CrossEncoderService()
    )

    print(
        "✓ Cross-encoder initialized."
    )

    # ========================================================
    # 5. PROCESS QUESTIONS
    # ========================================================

    evaluation_results = []

    total = len(
        labeled_records
    )

    for question_number, record in enumerate(
        labeled_records,
        start=1,
    ):

        print("\n")
        print("=" * 80)

        print(
            f"QUESTION "
            f"{question_number}/{total}"
        )

        print("=" * 80)

        benchmark_id = record.get(
            "benchmark_id"
        )

        question_text = (
            record.get(
                "text",
                ""
            )
            .strip()
        )

        subject_code = record.get(
            "subject_code"
        )

        print(
            f"Benchmark ID : "
            f"{benchmark_id}"
        )

        print(
            f"Course       : "
            f"{subject_code}"
        )

        print(
            f"Exam Type    : "
            f"{record.get('exam_type')}"
        )

        print(
            f"Question No. : "
            f"{record.get('question_number')}"
        )

        if record.get(
            "sub_question"
        ):

            print(
                f"Sub-question: "
                f"{record.get('sub_question')}"
            )

        print(
            "\nQuestion:"
        )

        print(
            "-" * 80
        )

        print(
            question_text
        )

        print(
            "-" * 80
        )

        # ====================================================
        # TIMER
        # ====================================================

        start_time = (
            time.perf_counter()
        )

        # ====================================================
        # M6.4 HYBRID RETRIEVAL
        # ====================================================

        print(
            "\nRunning hybrid retrieval..."
        )

        hybrid_results = (
            hybrid.search(
                query=question_text,
                n_results=HYBRID_TOP_K,
                course_code=subject_code,
            )
        )

        print(
            f"✓ Retrieved "
            f"{len(hybrid_results)} "
            f"candidates."
        )

        if not hybrid_results:

            raise RuntimeError(
                f"Hybrid retrieval returned "
                f"zero candidates for "
                f"{benchmark_id}"
            )

        # ====================================================
        # M6.5 CROSS-ENCODER
        # ====================================================

        print(
            "\nRunning cross-encoder reranking..."
        )

        reranked_results = (
            reranker.rerank(
                question_text,
                hybrid_results,
                top_k=RERANK_TOP_K,
            )
        )

        print(
            f"✓ Reranked "
            f"{len(reranked_results)} "
            f"candidates."
        )

        if not reranked_results:

            raise RuntimeError(
                f"Cross-encoder returned "
                f"zero candidates for "
                f"{benchmark_id}"
            )

        # ====================================================
        # M6.6.1 CONFIDENCE SIGNALS
        # ====================================================

        print(
            "\nExtracting confidence signals..."
        )

        signals = (
            extract_confidence_signals(
                reranked_results
            )
        )

        # ====================================================
        # TOP-1 PREDICTION
        # ====================================================

        top_candidate = (
            reranked_results[0]
        )

        prediction = (
            build_prediction(
                top_candidate
            )
        )

        # ====================================================
        # GROUND TRUTH
        # ====================================================

        ground_truth = (
            record[
                "ground_truth"
            ]
        )

        # ====================================================
        # EVALUATION
        # ====================================================

        evaluation = (
            evaluate_prediction(
                ground_truth,
                prediction,
                reranked_results,
            )
        )

        # ====================================================
        # LATENCY
        # ====================================================

        elapsed = (
            time.perf_counter()
            - start_time
        )

        # ====================================================
        # PRESERVE ALL CANDIDATES
        # ====================================================

        candidates = [

            build_candidate_output(
                candidate
            )

            for candidate
            in reranked_results
        ]

        # ====================================================
        # BUILD RESULT
        # ====================================================

        result = {

            "benchmark_id": (
                benchmark_id
            ),

            "question": (
                question_text
            ),

            "subject": (
                record.get(
                    "subject"
                )
            ),

            "subject_code": (
                subject_code
            ),

            "exam_type": (
                record.get(
                    "exam_type"
                )
            ),

            "question_number": (
                record.get(
                    "question_number"
                )
            ),

            "sub_question": (
                record.get(
                    "sub_question"
                )
            ),

            "ground_truth": (
                ground_truth
            ),

            "prediction": (
                prediction
            ),

            "evaluation": (
                evaluation
            ),

            "confidence_signals": (
                signals
            ),

            "reranked_candidates": (
                candidates
            ),

            "latency_seconds": (
                elapsed
            ),
        }

        evaluation_results.append(
            result
        )

        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        print("\n")
        print("-" * 80)
        print("RESULT")
        print("-" * 80)

        print(
            f"Ground truth : "
            f"{ground_truth.get('index_id')}"
        )

        print(
            f"Prediction   : "
            f"{prediction.get('index_id')}"
        )

        print(
            f"Index correct: "
            f"{evaluation['index_correct']}"
        )

        print(
            f"Unit correct : "
            f"{evaluation['unit_correct']}"
        )

        print(
            f"Topic correct: "
            f"{evaluation['topic_correct']}"
        )

        print(
            f"Subtopic correct: "
            f"{evaluation['subtopic_correct']}"
        )

        print(
            f"GT rank      : "
            f"{evaluation['ground_truth_rank']}"
        )

        print(
            f"Top-1 score  : "
            f"{signals['top1_score']:.6f}"
        )

        print(
            f"Top1-Top2 gap: "
            f"{signals['top1_top2_gap']:.6f}"
        )

        if (
            signals["top1_top2_ratio"]
            is not None
        ):

            print(
                f"Top1/Top2    : "
                f"{signals['top1_top2_ratio']:.6f}"
            )

        else:

            print(
                "Top1/Top2    : N/A"
            )

        print(
            f"BGE rank     : "
            f"{signals['bge_rank']}"
        )

        print(
            f"BM25 rank    : "
            f"{signals['bm25_rank']}"
        )

        print(
            f"BGE/BM25     : "
            f"{signals['bge_bm25_agree']}"
        )

        print(
            f"Latency      : "
            f"{elapsed:.3f}s"
        )

        # ====================================================
        # SAVE PROGRESS
        # ====================================================

        summary = (
            calculate_summary(
                evaluation_results
            )
        )

        output = {

            "benchmark_file": (
                str(BENCHMARK_FILE)
            ),

            "original_benchmark_size": (
                len(benchmark_records)
            ),

            "evaluated_questions": (
                len(evaluation_results)
            ),

            "skipped_unlabeled_questions": (
                unlabeled_ids
            ),

            "summary": (
                summary
            ),

            "results": (
                evaluation_results
            ),
        }

        save_json(
            OUTPUT_FILE,
            output,
        )

        print(
            f"\n✓ Progress saved to:"
            f"\n{OUTPUT_FILE}"
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    summary = (
        calculate_summary(
            evaluation_results
        )
    )

    print("\n")
    print("=" * 80)

    print(
        "M6.6.2 BATCH EVALUATION COMPLETED"
    )

    print("=" * 80)

    print(
        f"\nOriginal benchmark : "
        f"{len(benchmark_records)}"
    )

    print(
        f"Evaluated          : "
        f"{len(evaluation_results)}"
    )

    print(
        f"Skipped            : "
        f"{len(unlabeled_ids)}"
    )

    print(
        "\n"
    )

    print(
        f"Index accuracy     : "
        f"{summary['index_accuracy']:.4f}"
    )

    print(
        f"Unit accuracy      : "
        f"{summary['unit_accuracy']:.4f}"
    )

    print(
        f"Topic accuracy     : "
        f"{summary['topic_accuracy']:.4f}"
    )

    print(
        f"Subtopic accuracy  : "
        f"{summary['subtopic_accuracy']:.4f}"
    )

    print(
        "\n"
    )

    print(
        f"Recall@1           : "
        f"{summary['recall_at_1']:.4f}"
    )

    print(
        f"Recall@3           : "
        f"{summary['recall_at_3']:.4f}"
    )

    print(
        f"Recall@5           : "
        f"{summary['recall_at_5']:.4f}"
    )

    print(
        f"Recall@10          : "
        f"{summary['recall_at_10']:.4f}"
    )

    print(
        f"MRR                : "
        f"{summary['mrr']:.4f}"
    )

    print(
        f"\nOutput:"
        f"\n{OUTPUT_FILE}"
    )

    print("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()