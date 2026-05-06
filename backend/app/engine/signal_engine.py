from __future__ import annotations

from dataclasses import dataclass

from .scorer import RuleBasedScorer


@dataclass(frozen=True)
class SignalResult:
    decision: str
    score: int
    buy_confirmations: int
    sell_confirmations: int


class SignalEngine:
    """Combines indicator outputs into BUY / SELL / WAIT decisions.

    Confirmation system:
    - BUY requires at least 2 bullish confirmations.
    - SELL requires at least 2 bearish confirmations.

    Score system:
    - BUY when score >= 3 and confirmations condition is met.
    - SELL when score <= -3 and confirmations condition is met.
    - WAIT otherwise.
    """

    def __init__(self, scorer: RuleBasedScorer | None = None) -> None:
        self.scorer = scorer or RuleBasedScorer()

    def evaluate(self, indicator_outputs: dict[str, int]) -> SignalResult:
        score, buy_confirmations, sell_confirmations = self.scorer.score(indicator_outputs)

        if score >= 3 and buy_confirmations >= 2:
            decision = "BUY"
        elif score <= -3 and sell_confirmations >= 2:
            decision = "SELL"
        else:
            decision = "WAIT"

        return SignalResult(
            decision=decision,
            score=score,
            buy_confirmations=buy_confirmations,
            sell_confirmations=sell_confirmations,
        )
