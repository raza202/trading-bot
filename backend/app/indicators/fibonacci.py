from __future__ import annotations


def _find_confirmed_swing(prices: list[float], lookback: int = 5) -> tuple[float, float] | None:
    if len(prices) <= lookback * 2:
        return None

    confirmed = prices[:-lookback]
    if len(confirmed) < lookback + 2:
        return None

    swing_high = max(confirmed[-(lookback + 20):]) if len(confirmed) > lookback + 20 else max(confirmed)
    swing_low = min(confirmed[-(lookback + 20):]) if len(confirmed) > lookback + 20 else min(confirmed)
    return swing_high, swing_low


def analyze_fibonacci(closes: list[float]) -> dict[str, float | None]:
    swing = _find_confirmed_swing(closes)
    if swing is None:
        return {"fib_swing_high": None, "fib_swing_low": None, "fib_level_382": None, "fib_level_618": None}

    swing_high, swing_low = swing
    high = max(swing_high, swing_low)
    low = min(swing_high, swing_low)

    if high == low:
        return {"fib_swing_high": high, "fib_swing_low": low, "fib_level_382": None, "fib_level_618": None}

    span = high - low
    return {
        "fib_swing_high": high,
        "fib_swing_low": low,
        "fib_level_382": high - (0.382 * span),
        "fib_level_618": high - (0.618 * span),
    }
