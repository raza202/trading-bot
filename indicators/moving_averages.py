from __future__ import annotations


def _sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    window = values[-period:]
    return sum(window) / period


def _ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None

    k = 2 / (period + 1)
    ema = sum(values[:period]) / period
    for price in values[period:]:
        ema = (price - ema) * k + ema
    return ema


def analyze_moving_averages(closes: list[float]) -> dict[str, str | float]:
    """
    Fixed settings:
    - EMA 9
    - EMA 21
    - EMA 50
    - SMA 200
    """
    if len(closes) < 200:
        return {
            "signal": "NONE",
            "strength": 0.0,
            "reason": "Not enough data for SMA 200 (need at least 200 closes).",
        }

    ema9 = _ema(closes, 9)
    ema21 = _ema(closes, 21)
    ema50 = _ema(closes, 50)
    sma200 = _sma(closes, 200)

    assert ema9 is not None and ema21 is not None and ema50 is not None and sma200 is not None

    bullish_stack = ema9 > ema21 > ema50 > sma200
    bearish_stack = ema9 < ema21 < ema50 < sma200

    if bullish_stack:
        spread = (ema9 - sma200) / sma200 if sma200 else 0.0
        return {
            "signal": "BUY",
            "strength": min(1.0, max(0.0, spread * 8)),
            "reason": "Bullish MA alignment: EMA9 > EMA21 > EMA50 > SMA200.",
        }

    if bearish_stack:
        spread = (sma200 - ema9) / sma200 if sma200 else 0.0
        return {
            "signal": "SELL",
            "strength": min(1.0, max(0.0, spread * 8)),
            "reason": "Bearish MA alignment: EMA9 < EMA21 < EMA50 < SMA200.",
        }

    return {
        "signal": "NONE",
        "strength": 0.25,
        "reason": "No clear MA alignment.",
    }
