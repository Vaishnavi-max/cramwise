from typing import Any


class ConfidencePolicyService:
    """
    M6.6.4

    Converts confidence signals produced by M6.6.1
    into a three-way decision:

        HIGH
        MEDIUM
        LOW

    IMPORTANT:
    The thresholds are configuration parameters.
    They should be selected using benchmark evaluation,
    not blindly assumed to be optimal.
    """

    def __init__(
        self,
        high_score_threshold: float = 0.35,
        high_gap_threshold: float = 0.20,
        medium_score_threshold: float = 0.15,
        medium_gap_threshold: float = 0.05,
    ):
        self.high_score_threshold = (
            high_score_threshold
        )

        self.high_gap_threshold = (
            high_gap_threshold
        )

        self.medium_score_threshold = (
            medium_score_threshold
        )

        self.medium_gap_threshold = (
            medium_gap_threshold
        )

    # ======================================================
    # HIGH CONFIDENCE
    # ======================================================

    def is_high_confidence(
        self,
        signals: dict[str, Any],
    ) -> bool:
        """
        HIGH confidence requires strong evidence.

        Current experimental rule:

            BGE/BM25 agree
            AND
            Top-1 reranker score is strong
            AND
            Top1-Top2 gap is sufficiently large
        """

        score = signals.get(
            "top1_score"
        )

        gap = signals.get(
            "top1_top2_gap"
        )

        agreement = signals.get(
            "bge_bm25_agree",
            False,
        )

        if score is None:
            return False

        if gap is None:
            return False

        return (
            agreement
            and score
            >= self.high_score_threshold
            and gap
            >= self.high_gap_threshold
        )

    # ======================================================
    # LOW CONFIDENCE
    # ======================================================

    def is_low_confidence(
        self,
        signals: dict[str, Any],
    ) -> bool:
        """
        LOW confidence means retrieval evidence
        is weak or highly uncertain.

        Current experimental rule:

        1. Very weak reranker score

        OR

        2. Both score and gap are weak

        OR

        3. BGE/BM25 disagree AND the score is weak
        """

        score = signals.get(
            "top1_score"
        )

        gap = signals.get(
            "top1_top2_gap"
        )

        agreement = signals.get(
            "bge_bm25_agree",
            False,
        )

        if score is None:
            return True

        if gap is None:
            return True

        # Very weak candidate
        if (
            score
            < self.medium_score_threshold
        ):
            return True

        # Weak score + weak separation
        if (
            score
            < self.high_score_threshold
            and gap
            < self.medium_gap_threshold
        ):
            return True

        # Retriever disagreement + weak score
        if (
            not agreement
            and score
            < self.high_score_threshold
        ):
            return True

        return False

    # ======================================================
    # FINAL DECISION
    # ======================================================

    def decide(
        self,
        signals: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return the final confidence decision.

        Possible decisions:

            HIGH
            MEDIUM
            LOW

        Routing:

            HIGH   -> ACCEPT
            MEDIUM -> LLM_VERIFY
            LOW    -> ABSTAIN
        """

        if self.is_high_confidence(
            signals
        ):

            return {
                "confidence_level": "HIGH",
                "decision": "ACCEPT",
                "reason": (
                    "Strong reranker score, "
                    "large Top1-Top2 separation, "
                    "and BGE/BM25 agreement."
                ),
            }

        if self.is_low_confidence(
            signals
        ):

            return {
                "confidence_level": "LOW",
                "decision": "ABSTAIN",
                "reason": (
                    "Retrieval evidence is "
                    "too weak or ambiguous."
                ),
            }

        return {
            "confidence_level": "MEDIUM",
            "decision": "LLM_VERIFY",
            "reason": (
                "Candidate is plausible but "
                "retrieval evidence is not "
                "strong enough for automatic "
                "acceptance."
            ),
        }