from __future__ import annotations


def analyze_trendline(closes: list[float], window: int = 6) -> dict[str, float | int | None]:
    if len(closes) < window:
        return {"trend_up_ratio": None, "trend_down_ratio": None, "window": window}

    recent = closes[-window:]
    highs = [recent[i] for i in range(1, len(recent)) if recent[i] > recent[i - 1]]
    lows = [recent[i] for i in range(1, len(recent)) if recent[i] < recent[i - 1]]

    bullish_score = len(highs) / (window - 1)
    bearish_score = len(lows) / (window - 1)

    return {"trend_up_ratio": bullish_score, "trend_down_ratio": bearish_score, "window": window}
