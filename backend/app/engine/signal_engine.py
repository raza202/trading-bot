from __future__ import annotations

from dataclasses import dataclass

from .scorer import RuleBasedScorer


@dataclass(frozen=True)
class SignalResult:
    signal: str
    confidence: float
    score: int
    buy_confirmations: int
    sell_confirmations: int
    trace: dict[str, object]


class SignalEngine:
    """Single source of truth for BUY/SELL/WAIT decisions."""

    REQUIRED_VOTES = frozenset(RuleBasedScorer.DEFAULT_WEIGHTS.keys())

    def __init__(self, scorer: RuleBasedScorer | None = None) -> None:
        self.scorer = scorer or RuleBasedScorer()

    def evaluate(self, indicator_votes: dict[str, int]) -> SignalResult:
        missing = self.REQUIRED_VOTES - set(indicator_votes.keys())
        if missing:
            raise ValueError(f"Missing indicator votes: {', '.join(sorted(missing))}")

        score, buy_confirmations, sell_confirmations, weighted_scores = self.scorer.score(indicator_votes)

        if score >= 3 and buy_confirmations >= 2:
            signal = "BUY"
        elif score <= -3 and sell_confirmations >= 2:
            signal = "SELL"
        else:
            signal = "WAIT"

        confidence = min(1.0, abs(score) / 7)
        decision_path = (
            f"score={score}, buy_confirmations={buy_confirmations}, "
            f"sell_confirmations={sell_confirmations}, threshold=±3"
        )

        return SignalResult(
            signal=signal,
            confidence=round(confidence, 4),
            score=score,
            buy_confirmations=buy_confirmations,
            sell_confirmations=sell_confirmations,
            trace={
                "indicators_used": sorted(indicator_votes.keys()),
                "votes": indicator_votes,
                "scores": weighted_scores,
                "final_decision_path": decision_path,
            },
        )
