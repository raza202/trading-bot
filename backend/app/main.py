from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI, HTTPException

app = FastAPI(title="IKRAAZ Trading Bot API")

Timeframe = Literal["15m", "30m", "1h"]
SignalType = Literal["BUY", "SELL", "WAIT"]


TOP_PSX_STOCKS = [
    {"symbol": "OGDC", "name": "Oil & Gas Development Co.", "price": 133.5},
    {"symbol": "PPL", "name": "Pakistan Petroleum Ltd.", "price": 109.2},
    {"symbol": "PSO", "name": "Pakistan State Oil", "price": 177.1},
    {"symbol": "HBL", "name": "Habib Bank Ltd.", "price": 124.9},
    {"symbol": "UBL", "name": "United Bank Ltd.", "price": 184.4},
    {"symbol": "MCB", "name": "MCB Bank Ltd.", "price": 235.7},
    {"symbol": "ENGRO", "name": "Engro Corporation", "price": 316.8},
    {"symbol": "LUCK", "name": "Lucky Cement", "price": 737.0},
    {"symbol": "FFC", "name": "Fauji Fertilizer Co.", "price": 142.6},
    {"symbol": "SYS", "name": "Systems Ltd.", "price": 418.2},
]

SIGNAL_BY_SYMBOL: dict[str, dict[str, float | SignalType]] = {
    "OGDC": {"signal": "BUY", "confidence": 0.81},
    "PPL": {"signal": "BUY", "confidence": 0.74},
    "PSO": {"signal": "WAIT", "confidence": 0.58},
    "HBL": {"signal": "SELL", "confidence": 0.69},
    "UBL": {"signal": "BUY", "confidence": 0.76},
    "MCB": {"signal": "WAIT", "confidence": 0.54},
    "ENGRO": {"signal": "BUY", "confidence": 0.79},
    "LUCK": {"signal": "SELL", "confidence": 0.72},
    "FFC": {"signal": "WAIT", "confidence": 0.56},
    "SYS": {"signal": "BUY", "confidence": 0.84},
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "IKRAAZ ENGINE RUNNING"}


@app.get("/stocks")
def stocks() -> list[dict[str, str | float]]:
    return TOP_PSX_STOCKS


@app.get("/stock/{symbol}")
def stock(symbol: str) -> dict[str, str | float | SignalType]:
    normalized = symbol.upper()
    stock_data = next((item for item in TOP_PSX_STOCKS if item["symbol"] == normalized), None)
    if stock_data is None:
        raise HTTPException(status_code=404, detail=f"Symbol '{normalized}' not found")

    signal_data = SIGNAL_BY_SYMBOL.get(normalized, {"signal": "WAIT", "confidence": 0.5})
    return {
        **stock_data,
        "signal": signal_data["signal"],
        "confidence": signal_data["confidence"],
    }


@app.get("/signals")
def signals() -> dict[str, object]:
    return {
        "timeframe": "15m",
        "updated_at": datetime.now(UTC).isoformat(),
        "signals": [
            {
                **stock,
                "signal": SIGNAL_BY_SYMBOL[stock["symbol"]]["signal"],
                "confidence": SIGNAL_BY_SYMBOL[stock["symbol"]]["confidence"],
            }
            for stock in TOP_PSX_STOCKS
        ],
    }


@app.get("/timeframe/{timeframe}")
def timeframe(timeframe: Timeframe) -> dict[str, object]:
    multiplier_by_tf = {"15m": 1.0, "30m": 0.96, "1h": 0.92}
    multiplier = multiplier_by_tf[timeframe]

    adjusted_signals = []
    for stock in TOP_PSX_STOCKS:
        base = SIGNAL_BY_SYMBOL[stock["symbol"]]
        adjusted_signals.append(
            {
                **stock,
                "signal": base["signal"],
                "confidence": round(float(base["confidence"]) * multiplier, 2),
            }
        )

    return {
        "timeframe": timeframe,
        "updated_at": datetime.now(UTC).isoformat(),
        "signals": adjusted_signals,
    }
