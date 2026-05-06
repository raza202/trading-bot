from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorVote:
    name: str
    value: int


class RuleBasedScorer:
    """Scores normalized indicator votes using explicit weights."""

    DEFAULT_WEIGHTS: dict[str, int] = {
        "moving_averages": 2,
        "rsi": 1,
        "fibonacci": 1,
        "candlesticks": 1,
        "trendline": 2,
    }

    def __init__(self, weights: dict[str, int] | None = None) -> None:
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)

    def score(self, indicator_votes: dict[str, int]) -> tuple[int, int, int, dict[str, int]]:
        unknown = [key for key in indicator_votes if key not in self.weights]
        if unknown:
            raise ValueError(f"Unknown indicator keys: {', '.join(sorted(unknown))}")

        weighted_scores: dict[str, int] = {}
        total_score = 0
        buy_confirmations = 0
        sell_confirmations = 0

        for name, vote in indicator_votes.items():
            if vote not in (-1, 0, 1):
                raise ValueError(f"Invalid vote '{vote}' for '{name}'. Expected -1, 0, or 1.")

            if vote > 0:
                buy_confirmations += 1
            elif vote < 0:
                sell_confirmations += 1

            weighted = vote * self.weights[name]
            weighted_scores[name] = weighted
            total_score += weighted

        return total_score, buy_confirmations, sell_confirmations, weighted_scores
