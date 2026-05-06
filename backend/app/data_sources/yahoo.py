from __future__ import annotations

from .base import DataSource, OHLCV


class YahooDataSource(DataSource):
    """Yahoo Finance source (requires yfinance)."""

    def fetch_ohlcv(self, symbol: str, interval: str = "1d", limit: int = 100) -> OHLCV:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError(
                "YahooDataSource requires the 'yfinance' package. Install it to enable Yahoo integration."
            ) from exc

        period = "max" if limit > 730 else "2y"
        df = yf.Ticker(symbol).history(period=period, interval=interval)

        if df.empty:
            return {"timestamp": [], "open": [], "high": [], "low": [], "close": [], "volume": []}

        df = df.tail(limit)

        timestamps = [int(idx.to_pydatetime().timestamp()) for idx in df.index]

        return {
            "timestamp": timestamps,
            "open": [float(v) for v in df["Open"].tolist()],
            "high": [float(v) for v in df["High"].tolist()],
            "low": [float(v) for v in df["Low"].tolist()],
            "close": [float(v) for v in df["Close"].tolist()],
            "volume": [float(v) for v in df["Volume"].tolist()],
        }
