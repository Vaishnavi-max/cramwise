# app/services/confidence_service.py


class ConfidenceService:
    """
    Extracts confidence-related signals from
    M6.5 cross-encoder reranking results.

    IMPORTANT:
    This service does NOT make HIGH / MEDIUM / LOW
    decisions yet.

    It only calculates measurable signals that will
    later be used to design the confidence decision layer.
    """

    # ------------------------------------------------------
    # SIGNAL EXTRACTION
    # ------------------------------------------------------

    def calculate_signals(
        self,
        reranked_candidates: list[dict],
    ) -> dict:
        """
        Calculate confidence signals from reranked
        candidates.

        Candidates must already be sorted by:

            reranker_rank

        with rank 1 representing the best candidate.
        """

        if not reranked_candidates:
            raise ValueError(
                "Reranked candidate list cannot be empty."
            )

        # --------------------------------------------------
        # 1. Validate required fields
        # --------------------------------------------------

        required_fields = {
            "reranker_score",
            "reranker_rank",
            "hybrid_rank",
            "bge_rank",
            "bm25_rank",
        }

        for candidate in reranked_candidates:

            missing_fields = (
                required_fields
                - candidate.keys()
            )

            if missing_fields:

                raise ValueError(
                    "Candidate "
                    f"{candidate.get('index_id')} "
                    "is missing required fields: "
                    f"{sorted(missing_fields)}"
                )

        # --------------------------------------------------
        # 2. Top candidate
        # --------------------------------------------------

        top1 = reranked_candidates[0]

        top1_score = float(
            top1["reranker_score"]
        )

        top1_reranker_rank = int(
            top1["reranker_rank"]
        )

        top1_hybrid_rank = int(
            top1["hybrid_rank"]
        )

        top1_bge_rank = (
            int(top1["bge_rank"])
            if top1["bge_rank"] is not None
            else None
        )

        top1_bm25_rank = (
            int(top1["bm25_rank"])
            if top1["bm25_rank"] is not None
            else None
        )

        # --------------------------------------------------
        # 3. Top-2 candidate
        # --------------------------------------------------

        top2 = (
            reranked_candidates[1]
            if len(reranked_candidates) >= 2
            else None
        )

        top2_score = (
            float(top2["reranker_score"])
            if top2 is not None
            else None
        )

        # --------------------------------------------------
        # 4. Top-3 candidate
        # --------------------------------------------------

        top3 = (
            reranked_candidates[2]
            if len(reranked_candidates) >= 3
            else None
        )

        top3_score = (
            float(top3["reranker_score"])
            if top3 is not None
            else None
        )

        # --------------------------------------------------
        # 5. Top-1 / Top-2 gap
        # --------------------------------------------------

        top1_top2_gap = (
            top1_score - top2_score
            if top2_score is not None
            else None
        )

        # --------------------------------------------------
        # 6. Top-1 / Top-2 ratio
        # --------------------------------------------------

        if (
            top2_score is not None
            and top2_score > 0
        ):

            top1_top2_ratio = (
                top1_score / top2_score
            )

        else:

            top1_top2_ratio = None

        # --------------------------------------------------
        # 7. Top-1 / Top-3 gap
        # --------------------------------------------------

        top1_top3_gap = (
            top1_score - top3_score
            if top3_score is not None
            else None
        )

        # --------------------------------------------------
        # 8. BGE / BM25 agreement
        # --------------------------------------------------

        bge_bm25_agree = (
            top1_bge_rank is not None
            and top1_bm25_rank is not None
        )

        # --------------------------------------------------
        # 9. Both retrievers found Top-1
        # --------------------------------------------------

        retrieved_by_both = (
            top1_bge_rank is not None
            and top1_bm25_rank is not None
        )

        # --------------------------------------------------
        # 10. Score distribution
        # --------------------------------------------------

        reranker_scores = [
            float(
                candidate[
                    "reranker_score"
                ]
            )
            for candidate
            in reranked_candidates
        ]

        # --------------------------------------------------
        # 11. Score statistics
        # --------------------------------------------------

        score_min = min(
            reranker_scores
        )

        score_max = max(
            reranker_scores
        )

        score_mean = (
            sum(reranker_scores)
            / len(reranker_scores)
        )

        # --------------------------------------------------
        # 12. Return signals
        # --------------------------------------------------

        return {
            "top1_score": top1_score,
            "top2_score": top2_score,
            "top3_score": top3_score,

            "top1_top2_gap": (
                top1_top2_gap
            ),

            "top1_top2_ratio": (
                top1_top2_ratio
            ),

            "top1_top3_gap": (
                top1_top3_gap
            ),

            "top1_reranker_rank": (
                top1_reranker_rank
            ),

            "top1_hybrid_rank": (
                top1_hybrid_rank
            ),

            "top1_bge_rank": (
                top1_bge_rank
            ),

            "top1_bm25_rank": (
                top1_bm25_rank
            ),

            "bge_bm25_agree": (
                bge_bm25_agree
            ),

            "retrieved_by_both": (
                retrieved_by_both
            ),

            "reranker_score_min": (
                score_min
            ),

            "reranker_score_max": (
                score_max
            ),

            "reranker_score_mean": (
                score_mean
            ),

            "num_candidates": (
                len(reranked_candidates)
            ),
        }