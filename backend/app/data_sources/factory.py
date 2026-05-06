from __future__ import annotations

import os

from .base import DataSource
from .mock_data import MockDataSource
from .tradingview import TradingViewDataSource
from .yahoo import YahooDataSource


def get_data_source(name: str | None = None) -> DataSource:
    """Return configured data source; default is mock for safety."""
    source_name = (name or os.getenv("DATA_SOURCE") or "mock").strip().lower()

    if source_name == "yahoo":
        return YahooDataSource()
    if source_name == "tradingview":
        return TradingViewDataSource(
            username=os.getenv("TRADINGVIEW_USERNAME"),
            password=os.getenv("TRADINGVIEW_PASSWORD"),
        )
    return MockDataSource()
