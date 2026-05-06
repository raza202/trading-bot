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


def analyze_candlesticks(candles: list[dict[str, float]]) -> dict[str, int]:
    if len(candles) < 2:
        return {"bullish_engulfing": 0, "bearish_engulfing": 0, "hammer": 0, "doji": 0}

    prev = candles[-2]
    last = candles[-1]
    o, h, l, c = last["open"], last["high"], last["low"], last["close"]
    po, pc = prev["open"], prev["close"]

    return {
        "bullish_engulfing": int(_is_bullish_engulfing(po, pc, o, c)),
        "bearish_engulfing": int(_is_bearish_engulfing(po, pc, o, c)),
        "hammer": int(_is_hammer(o, h, l, c)),
        "doji": int(_is_doji(o, h, l, c)),
    }
