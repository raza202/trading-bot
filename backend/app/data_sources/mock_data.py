from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .base import DataSource, OHLCV


class MockDataSource(DataSource):
    """Safe default source that returns deterministic synthetic OHLCV data."""

    def fetch_ohlcv(self, symbol: str, interval: str = "1d", limit: int = 100) -> OHLCV:
        step = timedelta(days=1)
        if interval.endswith("h"):
            step = timedelta(hours=int(interval[:-1]))
        elif interval.endswith("m"):
            step = timedelta(minutes=int(interval[:-1]))

        now = datetime.now(timezone.utc)
        start = now - (limit * step)

        timestamps: list[int] = []
        opens: list[float] = []
        highs: list[float] = []
        lows: list[float] = []
        closes: list[float] = []
        volumes: list[float] = []

        base_price = 100.0 + (abs(hash(symbol)) % 500) / 10

        for i in range(limit):
            ts = start + i * step
            drift = i * 0.15
            wave = ((i % 7) - 3) * 0.2

            o = base_price + drift + wave
            c = o + (((i % 3) - 1) * 0.3)
            h = max(o, c) + 0.4
            l = min(o, c) - 0.4
            v = 1_000 + (i * 25)

            timestamps.append(int(ts.timestamp()))
            opens.append(round(o, 4))
            highs.append(round(h, 4))
            lows.append(round(l, 4))
            closes.append(round(c, 4))
            volumes.append(float(v))

        return {
            "timestamp": timestamps,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
