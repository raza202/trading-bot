from __future__ import annotations

from .base import DataSource, OHLCV


class TradingViewDataSource(DataSource):
    """Optional TradingView source via tvDatafeed-compatible clients."""

    def __init__(self, username: str | None = None, password: str | None = None):
        self.username = username
        self.password = password

    def fetch_ohlcv(self, symbol: str, interval: str = "1d", limit: int = 100) -> OHLCV:
        try:
            from tvDatafeed import Interval, TvDatafeed  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "TradingViewDataSource requires 'tvDatafeed'. Install it to enable TradingView integration."
            ) from exc

        interval_map = {
            "1m": Interval.in_1_minute,
            "3m": Interval.in_3_minute,
            "5m": Interval.in_5_minute,
            "15m": Interval.in_15_minute,
            "30m": Interval.in_30_minute,
            "45m": Interval.in_45_minute,
            "1h": Interval.in_1_hour,
            "2h": Interval.in_2_hour,
            "3h": Interval.in_3_hour,
            "4h": Interval.in_4_hour,
            "1d": Interval.in_daily,
            "1w": Interval.in_weekly,
            "1M": Interval.in_monthly,
        }

        if interval not in interval_map:
            raise ValueError(f"Unsupported TradingView interval: {interval}")

        tv = TvDatafeed(username=self.username, password=self.password)
        df = tv.get_hist(symbol=symbol, exchange="", interval=interval_map[interval], n_bars=limit)

        if df is None or df.empty:
            return {"timestamp": [], "open": [], "high": [], "low": [], "close": [], "volume": []}

        return {
            "timestamp": [int(idx.to_pydatetime().timestamp()) for idx in df.index],
            "open": [float(v) for v in df["open"].tolist()],
            "high": [float(v) for v in df["high"].tolist()],
            "low": [float(v) for v in df["low"].tolist()],
            "close": [float(v) for v in df["close"].tolist()],
            "volume": [float(v) for v in df["volume"].tolist()],
        }
