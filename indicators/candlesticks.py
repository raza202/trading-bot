from __future__ import annotations


def _is_doji(o: float, h: float, l: float, c: float) -> bool:
    body = abs(c - o)
    rng = h - l
    return rng > 0 and (body / rng) <= 0.1


def _is_hammer(o: float, h: float, l: float, c: float) -> bool:
    body = abs(c - o)
    upper_shadow = h - max(o, c)
    lower_shadow = min(o, c) - l
    return lower_shadow >= body * 2 and upper_shadow <= body


def _is_bullish_engulfing(prev_o: float, prev_c: float, o: float, c: float) -> bool:
    return prev_c < prev_o and c > o and o <= prev_c and c >= prev_o


def _is_bearish_engulfing(prev_o: float, prev_c: float, o: float, c: float) -> bool:
    return prev_c > prev_o and c < o and o >= prev_c and c <= prev_o


def analyze_candlesticks(candles: list[dict[str, float]]) -> dict[str, str | float]:
    """Each candle must contain: open, high, low, close."""
    if len(candles) < 2:
        return {"signal": "NONE", "strength": 0.0, "reason": "Need at least 2 candles."}

    prev = candles[-2]
    last = candles[-1]
    o, h, l, c = last["open"], last["high"], last["low"], last["close"]
    po, pc = prev["open"], prev["close"]

    if _is_bullish_engulfing(po, pc, o, c):
        return {"signal": "BUY", "strength": 0.8, "reason": "Bullish engulfing detected."}

    if _is_bearish_engulfing(po, pc, o, c):
        return {"signal": "SELL", "strength": 0.8, "reason": "Bearish engulfing detected."}

    if _is_hammer(o, h, l, c):
        direction = "BUY" if c >= o else "NONE"
        return {
            "signal": direction,
            "strength": 0.65 if direction == "BUY" else 0.35,
            "reason": "Hammer candle detected.",
        }

    if _is_doji(o, h, l, c):
        return {"signal": "NONE", "strength": 0.3, "reason": "Doji detected (indecision)."}

    return {"signal": "NONE", "strength": 0.2, "reason": "No required candlestick pattern detected."}
