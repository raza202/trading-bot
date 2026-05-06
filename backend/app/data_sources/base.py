from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class OHLCV(TypedDict):
    timestamp: list[int]
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]


class DataSource(ABC):
    """Abstract data source for market candles."""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 100,
    ) -> OHLCV:
        """Fetch and normalize candle data into the standard OHLCV schema."""
        raise NotImplementedError
