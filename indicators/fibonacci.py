from __future__ import annotations


def _find_auto_swing(prices: list[float], lookback: int = 5) -> tuple[float, float] | None:
    if len(prices) < (lookback * 2) + 1:
        return None

    swing_highs: list[tuple[int, float]] = []
    swing_lows: list[tuple[int, float]] = []

    for i in range(lookback, len(prices) - lookback):
        center = prices[i]
        left = prices[i - lookback:i]
        right = prices[i + 1:i + 1 + lookback]

        if center >= max(left) and center >= max(right):
            swing_highs.append((i, center))
        if center <= min(left) and center <= min(right):
            swing_lows.append((i, center))

    if not swing_highs or not swing_lows:
        return None

    last_high = swing_highs[-1][1]
    last_low = swing_lows[-1][1]
    return last_high, last_low


def analyze_fibonacci(closes: list[float]) -> dict[str, str | float]:
    swing = _find_auto_swing(closes)
    if swing is None:
        return {
            "signal": "NONE",
            "strength": 0.0,
            "reason": "Unable to detect swing high/low automatically.",
        }

    swing_high, swing_low = swing
    if swing_high == swing_low:
        return {"signal": "NONE", "strength": 0.0, "reason": "Invalid swing range."}

    high = max(swing_high, swing_low)
    low = min(swing_high, swing_low)
    latest = closes[-1]
    span = high - low

    level_382 = high - (0.382 * span)
    level_618 = high - (0.618 * span)

    if latest <= level_618 and latest >= low:
        return {
            "signal": "BUY",
            "strength": min(1.0, (level_618 - latest) / span + 0.4),
            "reason": "Price is in deep Fibonacci retracement zone (near 61.8%).",
        }

    if latest >= level_382 and latest <= high:
        return {
            "signal": "SELL",
            "strength": min(1.0, (latest - level_382) / span + 0.3),
            "reason": "Price is near upper Fibonacci retracement zone (near 38.2% to swing high).",
        }

    return {
        "signal": "NONE",
        "strength": 0.25,
        "reason": "Price is between major Fibonacci decision zones.",
    }
