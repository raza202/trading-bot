from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorSignal:
    """Represents one indicator output and its directional vote."""

    name: str
    direction: int


class RuleBasedScorer:
    """Scores indicator confirmations using fixed, deterministic weights."""

    DEFAULT_WEIGHTS: dict[str, int] = {
        "ema_trend": 2,
        "rsi": 1,
        "fibonacci": 1,
        "candlestick": 1,
        "trendline": 2,
    }

    def __init__(self, weights: dict[str, int] | None = None) -> None:
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)

    def score(self, indicator_outputs: dict[str, int]) -> tuple[int, int, int]:
        """Return (total_score, buy_confirmations, sell_confirmations).

        indicator_outputs values must be one of:
        - 1 for bullish confirmation
        - -1 for bearish confirmation
        - 0 for neutral/no confirmation
        """

        total_score = 0
        buy_confirmations = 0
        sell_confirmations = 0

        for indicator_name, direction in indicator_outputs.items():
            if direction not in (-1, 0, 1):
                raise ValueError(
                    f"Invalid direction '{direction}' for '{indicator_name}'. "
                    "Expected -1, 0, or 1."
                )

            weight = self.weights.get(indicator_name, 0)
            total_score += direction * weight

            if direction > 0:
                buy_confirmations += 1
            elif direction < 0:
                sell_confirmations += 1

        return total_score, buy_confirmations, sell_confirmations
