import json
import statistics
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "uploads/temp/m6/confidence_evaluation_43.json"
)

OUTPUT_FILE = Path(
    "uploads/temp/m6/confidence_signal_analysis.json"
)


# ============================================================
# HELPERS
# ============================================================

def mean(values):
    """
    Return mean of a list.

    Returns None when the list is empty.
    """
    if not values:
        return None

    return statistics.mean(values)


def median(values):
    """
    Return median of a list.

    Returns None when the list is empty.
    """
    if not values:
        return None

    return statistics.median(values)


def percentage(numerator, denominator):
    """
    Calculate percentage safely.
    """
    if denominator == 0:
        return 0.0

    return (
        numerator / denominator
    ) * 100.0


def numeric_values(
    records,
    signal_name,
):
    """
    Extract numeric confidence signal values.
    """

    values = []

    for record in records:

        signals = record.get(
            "confidence_signals",
            {}
        )

        value = signals.get(
            signal_name
        )

        if (
            value is not None
            and isinstance(
                value,
                (int, float),
            )
        ):
            values.append(
                float(value)
            )

    return values


# ============================================================
# GROUP STATISTICS
# ============================================================

def calculate_group_statistics(
    records,
    group_name,
):
    """
    Calculate confidence statistics
    for either CORRECT or INCORRECT
    top-1 predictions.
    """

    total = len(records)

    top1_scores = numeric_values(
        records,
        "top1_score",
    )

    top1_top2_gaps = numeric_values(
        records,
        "top1_top2_gap",
    )

    top1_top2_ratios = numeric_values(
        records,
        "top1_top2_ratio",
    )

    top1_top3_gaps = numeric_values(
        records,
        "top1_top3_gap",
    )

    hybrid_ranks = numeric_values(
        records,
        "hybrid_rank",
    )

    bge_ranks = numeric_values(
        records,
        "bge_rank",
    )

    bm25_ranks = numeric_values(
        records,
        "bm25_rank",
    )

    reranker_ranks = numeric_values(
        records,
        "reranker_rank",
    )

    bge_bm25_agreements = 0
    retrieved_by_both = 0

    for record in records:

        signals = record.get(
            "confidence_signals",
            {}
        )

        if signals.get(
            "bge_bm25_agree",
            False,
        ):
            bge_bm25_agreements += 1

        if signals.get(
            "retrieved_by_both",
            False,
        ):
            retrieved_by_both += 1

    return {
        "group": group_name,

        "count": total,

        # --------------------------------------------------
        # RERANKER SCORE
        # --------------------------------------------------

        "top1_score": {
            "mean": mean(
                top1_scores
            ),
            "median": median(
                top1_scores
            ),
            "min": (
                min(top1_scores)
                if top1_scores
                else None
            ),
            "max": (
                max(top1_scores)
                if top1_scores
                else None
            ),
        },

        # --------------------------------------------------
        # SCORE GAP
        # --------------------------------------------------

        "top1_top2_gap": {
            "mean": mean(
                top1_top2_gaps
            ),
            "median": median(
                top1_top2_gaps
            ),
            "min": (
                min(top1_top2_gaps)
                if top1_top2_gaps
                else None
            ),
            "max": (
                max(top1_top2_gaps)
                if top1_top2_gaps
                else None
            ),
        },

        # --------------------------------------------------
        # SCORE RATIO
        # --------------------------------------------------

        "top1_top2_ratio": {
            "mean": mean(
                top1_top2_ratios
            ),
            "median": median(
                top1_top2_ratios
            ),
            "min": (
                min(top1_top2_ratios)
                if top1_top2_ratios
                else None
            ),
            "max": (
                max(top1_top2_ratios)
                if top1_top2_ratios
                else None
            ),
        },

        # --------------------------------------------------
        # TOP1 - TOP3 GAP
        # --------------------------------------------------

        "top1_top3_gap": {
            "mean": mean(
                top1_top3_gaps
            ),
            "median": median(
                top1_top3_gaps
            ),
            "min": (
                min(top1_top3_gaps)
                if top1_top3_gaps
                else None
            ),
            "max": (
                max(top1_top3_gaps)
                if top1_top3_gaps
                else None
            ),
        },

        # --------------------------------------------------
        # RETRIEVAL RANKS
        # --------------------------------------------------

        "average_ranks": {
            "hybrid": mean(
                hybrid_ranks
            ),
            "bge": mean(
                bge_ranks
            ),
            "bm25": mean(
                bm25_ranks
            ),
            "reranker": mean(
                reranker_ranks
            ),
        },

        # --------------------------------------------------
        # RETRIEVER AGREEMENT
        # --------------------------------------------------

        "bge_bm25_agreement": {
            "count": bge_bm25_agreements,
            "percentage": percentage(
                bge_bm25_agreements,
                total,
            ),
        },

        "retrieved_by_both": {
            "count": retrieved_by_both,
            "percentage": percentage(
                retrieved_by_both,
                total,
            ),
        },
    }


# ============================================================
# THRESHOLD ANALYSIS
# ============================================================

def threshold_analysis(
    records,
    signal_name,
    thresholds,
):
    """
    Evaluate how well a signal threshold
    separates correct from incorrect predictions.

    Example:

        top1_score >= 0.5

    We calculate:

        selected
        correct
        incorrect
        precision
        coverage
    """

    results = []

    total = len(records)

    for threshold in thresholds:

        selected = []

        for record in records:

            signals = record.get(
                "confidence_signals",
                {}
            )

            value = signals.get(
                signal_name
            )

            if value is None:
                continue

            if value >= threshold:

                selected.append(
                    record
                )

        selected_count = len(
            selected
        )

        correct_count = sum(
            1
            for record in selected
            if record.get(
                "evaluation",
                {}
            ).get(
                "top1_correct",
                False,
            )
        )

        incorrect_count = (
            selected_count
            - correct_count
        )

        precision = (
            correct_count
            / selected_count
            if selected_count
            else 0.0
        )

        coverage = (
            selected_count
            / total
            if total
            else 0.0
        )

        results.append(
            {
                "threshold": threshold,

                "selected": selected_count,

                "correct": correct_count,

                "incorrect": incorrect_count,

                "precision": precision,

                "precision_percentage": (
                    precision * 100.0
                ),

                "coverage": coverage,

                "coverage_percentage": (
                    coverage * 100.0
                ),
            }
        )

    return results


# ============================================================
# AGREEMENT ANALYSIS
# ============================================================

def agreement_analysis(records):

    groups = {
        "agreement": [],
        "disagreement": [],
    }

    for record in records:

        signals = record.get(
            "confidence_signals",
            {}
        )

        if signals.get(
            "bge_bm25_agree",
            False,
        ):
            groups[
                "agreement"
            ].append(record)
        else:
            groups[
                "disagreement"
            ].append(record)

    results = {}

    for name, group in groups.items():

        total = len(group)

        correct = sum(
            1
            for record in group
            if record.get(
                "evaluation",
                {}
            ).get(
                "top1_correct",
                False,
            )
        )

        results[name] = {
            "count": total,

            "correct": correct,

            "incorrect": (
                total - correct
            ),

            "accuracy": (
                correct / total
                if total
                else 0.0
            ),

            "accuracy_percentage": (
                correct / total * 100.0
                if total
                else 0.0
            ),
        }

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "M6.6.3 - CONFIDENCE SIGNAL ANALYSIS"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # 1. LOAD EVALUATION
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation file not found:\n"
            f"{INPUT_FILE}\n\n"
            "Make sure M6.6.2 batch evaluation "
            "has been completed first."
        )

    print(
        f"\nInput:\n{INPUT_FILE}"
    )

    data = json.loads(
        INPUT_FILE.read_text(
            encoding="utf-8"
        )
    )

    records = data.get(
        "results",
        []
    )

    if not records:

        raise ValueError(
            "No evaluation results found."
        )

    print(
        f"✓ Loaded {len(records)} evaluated questions."
    )

    # --------------------------------------------------------
    # 2. SPLIT CORRECT / INCORRECT
    # --------------------------------------------------------

    correct_records = []
    incorrect_records = []

    for record in records:

        evaluation = record.get(
            "evaluation",
            {}
        )

        if evaluation.get(
            "top1_correct",
            False,
        ):
            correct_records.append(
                record
            )
        else:
            incorrect_records.append(
                record
            )

    print(
        f"\nCorrect top-1 : "
        f"{len(correct_records)}"
    )

    print(
        f"Incorrect top-1 : "
        f"{len(incorrect_records)}"
    )

    # --------------------------------------------------------
    # 3. GROUP STATISTICS
    # --------------------------------------------------------

    print(
        "\nCalculating signal statistics..."
    )

    correct_stats = (
        calculate_group_statistics(
            correct_records,
            "CORRECT",
        )
    )

    incorrect_stats = (
        calculate_group_statistics(
            incorrect_records,
            "INCORRECT",
        )
    )

    # --------------------------------------------------------
    # 4. PRINT MAIN COMPARISON
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "CORRECT vs INCORRECT"
    )
    print("=" * 80)

    print(
        f"\n{'Signal':<30}"
        f"{'Correct':>15}"
        f"{'Incorrect':>15}"
    )

    print("-" * 65)

    print(
        f"{'Top-1 score mean':<30}"
        f"{correct_stats['top1_score']['mean']:>15.6f}"
        f"{incorrect_stats['top1_score']['mean']:>15.6f}"
    )

    print(
        f"{'Top-1 score median':<30}"
        f"{correct_stats['top1_score']['median']:>15.6f}"
        f"{incorrect_stats['top1_score']['median']:>15.6f}"
    )

    print(
        f"{'Top1-Top2 gap mean':<30}"
        f"{correct_stats['top1_top2_gap']['mean']:>15.6f}"
        f"{incorrect_stats['top1_top2_gap']['mean']:>15.6f}"
    )

    print(
        f"{'Top1-Top2 gap median':<30}"
        f"{correct_stats['top1_top2_gap']['median']:>15.6f}"
        f"{incorrect_stats['top1_top2_gap']['median']:>15.6f}"
    )

    print(
        f"{'Top1/Top2 ratio mean':<30}"
        f"{correct_stats['top1_top2_ratio']['mean']:>15.6f}"
        f"{incorrect_stats['top1_top2_ratio']['mean']:>15.6f}"
    )

    print(
        f"{'Top1-Top3 gap mean':<30}"
        f"{correct_stats['top1_top3_gap']['mean']:>15.6f}"
        f"{incorrect_stats['top1_top3_gap']['mean']:>15.6f}"
    )

    print(
        f"{'Hybrid rank mean':<30}"
        f"{correct_stats['average_ranks']['hybrid']:>15.4f}"
        f"{incorrect_stats['average_ranks']['hybrid']:>15.4f}"
    )

    print(
        f"{'BGE rank mean':<30}"
        f"{correct_stats['average_ranks']['bge']:>15.4f}"
        f"{incorrect_stats['average_ranks']['bge']:>15.4f}"
    )

    print(
        f"{'BM25 rank mean':<30}"
        f"{correct_stats['average_ranks']['bm25']:>15.4f}"
        f"{incorrect_stats['average_ranks']['bm25']:>15.4f}"
    )

    print(
        f"{'Reranker rank mean':<30}"
        f"{correct_stats['average_ranks']['reranker']:>15.4f}"
        f"{incorrect_stats['average_ranks']['reranker']:>15.4f}"
    )

    print(
        f"{'BGE/BM25 agreement %':<30}"
        f"{correct_stats['bge_bm25_agreement']['percentage']:>14.2f}%"
        f"{incorrect_stats['bge_bm25_agreement']['percentage']:>14.2f}%"
    )

    print(
        f"{'Retrieved by both %':<30}"
        f"{correct_stats['retrieved_by_both']['percentage']:>14.2f}%"
        f"{incorrect_stats['retrieved_by_both']['percentage']:>14.2f}%"
    )

    # --------------------------------------------------------
    # 5. THRESHOLD ANALYSIS
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "TOP-1 SCORE THRESHOLD ANALYSIS"
    )
    print("=" * 80)

    score_thresholds = [
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.60,
        0.70,
        0.80,
    ]

    score_threshold_results = (
        threshold_analysis(
            records,
            "top1_score",
            score_thresholds,
        )
    )

    print(
        f"\n{'Threshold':<12}"
        f"{'Selected':>10}"
        f"{'Correct':>10}"
        f"{'Wrong':>10}"
        f"{'Precision':>14}"
        f"{'Coverage':>14}"
    )

    print("-" * 72)

    for row in score_threshold_results:

        print(
            f"{row['threshold']:<12.2f}"
            f"{row['selected']:>10}"
            f"{row['correct']:>10}"
            f"{row['incorrect']:>10}"
            f"{row['precision_percentage']:>13.2f}%"
            f"{row['coverage_percentage']:>13.2f}%"
        )

    # --------------------------------------------------------
    # 6. GAP THRESHOLD ANALYSIS
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "TOP1-TOP2 GAP THRESHOLD ANALYSIS"
    )
    print("=" * 80)

    gap_thresholds = [
        0.01,
        0.02,
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.50,
        0.60,
    ]

    gap_threshold_results = (
        threshold_analysis(
            records,
            "top1_top2_gap",
            gap_thresholds,
        )
    )

    print(
        f"\n{'Threshold':<12}"
        f"{'Selected':>10}"
        f"{'Correct':>10}"
        f"{'Wrong':>10}"
        f"{'Precision':>14}"
        f"{'Coverage':>14}"
    )

    print("-" * 72)

    for row in gap_threshold_results:

        print(
            f"{row['threshold']:<12.2f}"
            f"{row['selected']:>10}"
            f"{row['correct']:>10}"
            f"{row['incorrect']:>10}"
            f"{row['precision_percentage']:>13.2f}%"
            f"{row['coverage_percentage']:>13.2f}%"
        )

    # --------------------------------------------------------
    # 7. RETRIEVER AGREEMENT
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "BGE / BM25 AGREEMENT ANALYSIS"
    )
    print("=" * 80)

    agreement_results = (
        agreement_analysis(
            records
        )
    )

    for group_name, result in (
        agreement_results.items()
    ):

        print(
            f"\n{group_name.upper()}"
        )

        print(
            f"Questions : "
            f"{result['count']}"
        )

        print(
            f"Correct   : "
            f"{result['correct']}"
        )

        print(
            f"Incorrect : "
            f"{result['incorrect']}"
        )

        print(
            f"Accuracy  : "
            f"{result['accuracy_percentage']:.2f}%"
        )

    # --------------------------------------------------------
    # 8. IDENTIFY STRONGEST SIGNALS
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "SIGNAL SEPARATION"
    )
    print("=" * 80)

    signal_separation = {}

    signal_pairs = [
        (
            "top1_score",
            "Top-1 score",
        ),
        (
            "top1_top2_gap",
            "Top1-Top2 gap",
        ),
        (
            "top1_top2_ratio",
            "Top1/Top2 ratio",
        ),
        (
            "top1_top3_gap",
            "Top1-Top3 gap",
        ),
    ]

    for signal_name, display_name in (
        signal_pairs
    ):

        correct_values = numeric_values(
            correct_records,
            signal_name,
        )

        incorrect_values = numeric_values(
            incorrect_records,
            signal_name,
        )

        correct_mean = mean(
            correct_values
        )

        incorrect_mean = mean(
            incorrect_values
        )

        if (
            correct_mean is not None
            and incorrect_mean is not None
        ):

            separation = (
                correct_mean
                - incorrect_mean
            )

        else:

            separation = None

        signal_separation[
            signal_name
        ] = {
            "display_name": display_name,
            "correct_mean": correct_mean,
            "incorrect_mean": incorrect_mean,
            "mean_separation": separation,
        }

        print(
            f"\n{display_name}"
        )

        print(
            f"Correct mean   : "
            f"{correct_mean:.6f}"
        )

        print(
            f"Incorrect mean : "
            f"{incorrect_mean:.6f}"
        )

        print(
            f"Separation     : "
            f"{separation:.6f}"
        )

    # --------------------------------------------------------
    # 9. SAVE ANALYSIS
    # --------------------------------------------------------

    output = {
        "input_file": str(
            INPUT_FILE
        ),

        "evaluated_questions": len(
            records
        ),

        "correct_top1": len(
            correct_records
        ),

        "incorrect_top1": len(
            incorrect_records
        ),

        "correct_statistics":
            correct_stats,

        "incorrect_statistics":
            incorrect_stats,

        "threshold_analysis": {
            "top1_score":
                score_threshold_results,

            "top1_top2_gap":
                gap_threshold_results,
        },

        "agreement_analysis":
            agreement_results,

        "signal_separation":
            signal_separation,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 80)
    print(
        "M6.6.3 CONFIDENCE SIGNAL ANALYSIS COMPLETED"
    )
    print("=" * 80)

    print(
        f"\nOutput:\n{OUTPUT_FILE}"
    )

    print(
        "\nNext step:"
    )

    print(
        "Use these real benchmark statistics "
        "to design M6.6.4 confidence thresholds."
    )


if __name__ == "__main__":
    main()