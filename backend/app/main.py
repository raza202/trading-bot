from __future__ import annotations

import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

ENV = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENV.lower() == "production"

app = FastAPI(
    title="IKRAAZ Trading Bot API",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url="/openapi.json" if not IS_PRODUCTION else None,
)

Timeframe = Literal["15m", "30m", "1h"]
SignalType = Literal["BUY", "SELL", "WAIT"]


class AlertRequest(BaseModel):
    recipient: EmailStr
    symbol: str = Field(min_length=1, max_length=10)


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


def get_stock_and_signal(symbol: str) -> tuple[dict[str, str | float], dict[str, float | SignalType]]:
    normalized = symbol.upper()
    stock_data = next((item for item in TOP_PSX_STOCKS if item["symbol"] == normalized), None)
    if stock_data is None:
        raise HTTPException(status_code=404, detail=f"Symbol '{normalized}' not found")
    signal_data = SIGNAL_BY_SYMBOL.get(normalized, {"signal": "WAIT", "confidence": 0.5})
    return stock_data, signal_data


def send_email_alert(recipient: str, symbol: str, signal: SignalType, confidence: float, price: float) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_sender = os.getenv("SMTP_SENDER", smtp_user or "")

    if not all([smtp_host, smtp_user, smtp_password, smtp_sender]):
        raise HTTPException(
            status_code=500,
            detail="SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER.",
        )

    msg = EmailMessage()
    msg["Subject"] = f"Trading Alert: {symbol} {signal}"
    msg["From"] = smtp_sender
    msg["To"] = recipient
    msg.set_content(
        f"Symbol: {symbol}\nSignal: {signal}\nConfidence: {confidence:.2f}\nPrice: {price}\nGenerated at: {datetime.now(timezone.utc).isoformat()}"
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "IKRAAZ ENGINE RUNNING", "environment": ENV}


@app.get("/stocks")
def stocks() -> list[dict[str, str | float]]:
    return TOP_PSX_STOCKS


@app.get("/stock/{symbol}")
def stock(symbol: str) -> dict[str, str | float | SignalType]:
    stock_data, signal_data = get_stock_and_signal(symbol)
    return {
        **stock_data,
        "signal": signal_data["signal"],
        "confidence": signal_data["confidence"],
    }


@app.get("/signals")
def signals() -> dict[str, object]:
    return {
        "timeframe": "15m",
        "updated_at": datetime.now(timezone.utc).isoformat(),
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
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "signals": adjusted_signals,
    }


@app.post("/alerts/email")
def create_email_alert(request: AlertRequest) -> dict[str, str | float]:
    stock_data, signal_data = get_stock_and_signal(request.symbol)
    send_email_alert(
        recipient=request.recipient,
        symbol=stock_data["symbol"],
        signal=signal_data["signal"],
        confidence=float(signal_data["confidence"]),
        price=float(stock_data["price"]),
    )
    return {
        "status": "sent",
        "recipient": request.recipient,
        "symbol": str(stock_data["symbol"]),
        "signal": str(signal_data["signal"]),
        "confidence": float(signal_data["confidence"]),
    }
