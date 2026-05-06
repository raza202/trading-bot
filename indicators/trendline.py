from __future__ import annotations


def analyze_trendline(closes: list[float], window: int = 6) -> dict[str, str | float]:
    """Simple trendline logic based on higher highs / lower lows only."""
    if len(closes) < window:
        return {"signal": "NONE", "strength": 0.0, "reason": f"Need at least {window} closes."}

    recent = closes[-window:]
    highs = [recent[i] for i in range(1, len(recent)) if recent[i] > recent[i - 1]]
    lows = [recent[i] for i in range(1, len(recent)) if recent[i] < recent[i - 1]]

    bullish_score = len(highs) / (window - 1)
    bearish_score = len(lows) / (window - 1)

    if bullish_score >= 0.7:
        return {
            "signal": "BUY",
            "strength": min(1.0, bullish_score),
            "reason": "Higher highs structure detected.",
        }

    if bearish_score >= 0.7:
        return {
            "signal": "SELL",
            "strength": min(1.0, bearish_score),
            "reason": "Lower lows structure detected.",
        }

    return {
        "signal": "NONE",
        "strength": max(bullish_score, bearish_score) * 0.5,
        "reason": "No clear higher-highs or lower-lows trendline structure.",
    }
