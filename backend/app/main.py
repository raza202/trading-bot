from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException

from .indicators.candlesticks import analyze_candlesticks
from .indicators.fibonacci import analyze_fibonacci
from .indicators.moving_averages import analyze_moving_averages
from .indicators.rsi import analyze_rsi
from .indicators.trendline import analyze_trendline

from .data_sources.base import OHLCV
from .data_sources.factory import get_data_source
from .engine.signal_engine import SignalEngine

ENV = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENV.lower() == "production"

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IKRAAZ Trading Bot API",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url="/openapi.json" if not IS_PRODUCTION else None,
)

Timeframe = Literal["15m", "30m", "1h"]

TOP_PSX_STOCKS = [
    {"symbol": "OGDC", "name": "Oil & Gas Development Co."},
    {"symbol": "PPL", "name": "Pakistan Petroleum Ltd."},
    {"symbol": "PSO", "name": "Pakistan State Oil"},
    {"symbol": "HBL", "name": "Habib Bank Ltd."},
    {"symbol": "UBL", "name": "United Bank Ltd."},
    {"symbol": "MCB", "name": "MCB Bank Ltd."},
    {"symbol": "ENGRO", "name": "Engro Corporation"},
    {"symbol": "LUCK", "name": "Lucky Cement"},
    {"symbol": "FFC", "name": "Fauji Fertilizer Co."},
    {"symbol": "SYS", "name": "Systems Ltd."},
]


def _validate_ohlcv(ohlcv: OHLCV) -> None:
    required_keys = ["timestamp", "open", "high", "low", "close", "volume"]
    for key in required_keys:
        if key not in ohlcv:
            raise ValueError(f"Missing OHLCV key: {key}")

    lengths = {key: len(ohlcv[key]) for key in required_keys}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"OHLCV lengths mismatch: {lengths}")

    timestamps = ohlcv["timestamp"]
    if timestamps != sorted(timestamps):
        raise ValueError("OHLCV timestamps are not ordered oldest -> newest")


def _build_indicator_outputs(ohlcv: OHLCV) -> tuple[dict[str, int], dict[str, object]]:
    closes = ohlcv["close"]
    candles = [
        {"open": ohlcv["open"][i], "high": ohlcv["high"][i], "low": ohlcv["low"][i], "close": ohlcv["close"][i]}
        for i in range(len(closes))
    ]

    ma = analyze_moving_averages(closes)
    rsi = analyze_rsi(closes)
    fib = analyze_fibonacci(closes)
    candlestick = analyze_candlesticks(candles)
    trend = analyze_trendline(closes)

    votes = {
        "moving_averages": 1 if all([ma["ema9"], ma["ema21"], ma["ema50"], ma["sma200"]]) and ma["ema9"] > ma["ema21"] > ma["ema50"] > ma["sma200"] else -1 if all([ma["ema9"], ma["ema21"], ma["ema50"], ma["sma200"]]) and ma["ema9"] < ma["ema21"] < ma["ema50"] < ma["sma200"] else 0,
        "rsi": 1 if isinstance(rsi["rsi"], float) and rsi["rsi"] < 30 else -1 if isinstance(rsi["rsi"], float) and rsi["rsi"] > 70 else 0,
        "fibonacci": 1 if fib["fib_level_618"] is not None and closes[-1] <= fib["fib_level_618"] else -1 if fib["fib_level_382"] is not None and closes[-1] >= fib["fib_level_382"] else 0,
        "candlesticks": 1 if candlestick["bullish_engulfing"] or candlestick["hammer"] else -1 if candlestick["bearish_engulfing"] else 0,
        "trendline": 1 if trend["trend_up_ratio"] is not None and trend["trend_up_ratio"] >= 0.7 else -1 if trend["trend_down_ratio"] is not None and trend["trend_down_ratio"] >= 0.7 else 0,
    }

    metrics = {
        "moving_averages": ma,
        "rsi": rsi,
        "fibonacci": fib,
        "candlesticks": candlestick,
        "trendline": trend,
    }
    return votes, metrics


def _analyze_symbol(symbol: str, timeframe: Timeframe) -> dict[str, object]:
    source = get_data_source()
    engine = SignalEngine()

    interval_map = {"15m": "15m", "30m": "30m", "1h": "1h"}
    ohlcv = source.fetch_ohlcv(symbol=symbol, interval=interval_map[timeframe], limit=250)
    _validate_ohlcv(ohlcv)

    if len(ohlcv["close"]) < 20:
        raise ValueError("Not enough candles to evaluate indicators")

    votes, metrics = _build_indicator_outputs(ohlcv)
    result = engine.evaluate(votes)

    return {
        "symbol": symbol,
        "price": ohlcv["close"][-1],
        "signal": result.signal,
        "confidence": result.confidence,
        "trace": {
            **result.trace,
            "raw_metrics": metrics,
            "latest_timestamp": ohlcv["timestamp"][-1],
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "IKRAAZ ENGINE RUNNING", "environment": ENV}


@app.get("/timeframe/{timeframe}")
def timeframe(timeframe: Timeframe) -> dict[str, object]:
    signals = []
    for stock in TOP_PSX_STOCKS:
        try:
            analysis = _analyze_symbol(stock["symbol"], timeframe)
            signals.append({**stock, **analysis})
        except Exception as exc:
            logger.exception("analysis_failed symbol=%s", stock["symbol"])
            raise HTTPException(status_code=500, detail=f"Analysis failed for {stock['symbol']}: {exc}") from exc

    return {"timeframe": timeframe, "updated_at": datetime.now(timezone.utc).isoformat(), "signals": signals}


@app.get("/stock/{symbol}")
def stock(symbol: str, timeframe: Timeframe = "15m") -> dict[str, object]:
    match = next((item for item in TOP_PSX_STOCKS if item["symbol"] == symbol.upper()), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol.upper()}' not found")

    try:
        analysis = _analyze_symbol(match["symbol"], timeframe)
    except Exception as exc:
        logger.exception("single_symbol_analysis_failed symbol=%s", symbol)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {**match, **analysis}
