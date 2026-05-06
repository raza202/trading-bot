from __future__ import annotations


def _compute_rsi(closes: list[float], period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None

    gains: list[float] = []
    losses: list[float] = []

    for i in range(1, period + 1):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    for i in range(period + 1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def analyze_rsi(closes: list[float], period: int = 14) -> dict[str, str | float]:
    if period != 14:
        return {
            "signal": "NONE",
            "strength": 0.0,
            "reason": "RSI period is fixed at 14.",
        }

    rsi = _compute_rsi(closes, period=14)
    if rsi is None:
        return {
            "signal": "NONE",
            "strength": 0.0,
            "reason": "Not enough data for RSI 14.",
        }

    if rsi < 30:
        strength = min(1.0, (30 - rsi) / 30)
        return {
            "signal": "BUY",
            "strength": strength,
            "reason": f"RSI14 is oversold at {rsi:.2f}.",
        }

    if rsi > 70:
        strength = min(1.0, (rsi - 70) / 30)
        return {
            "signal": "SELL",
            "strength": strength,
            "reason": f"RSI14 is overbought at {rsi:.2f}.",
        }

    return {
        "signal": "NONE",
        "strength": 0.2,
        "reason": f"RSI14 is neutral at {rsi:.2f}.",
    }
