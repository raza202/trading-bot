from __future__ import annotations


def _sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def _ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None

    k = 2 / (period + 1)
    ema = sum(values[:period]) / period
    for price in values[period:]:
        ema = (price - ema) * k + ema
    return ema


def analyze_moving_averages(closes: list[float]) -> dict[str, float | None]:
    ema9 = _ema(closes, 9)
    ema21 = _ema(closes, 21)
    ema50 = _ema(closes, 50)
    sma200 = _sma(closes, 200)
    latest_close = closes[-1] if closes else None

    return {
        "ema9": ema9,
        "ema21": ema21,
        "ema50": ema50,
        "sma200": sma200,
        "price": latest_close,
    }
