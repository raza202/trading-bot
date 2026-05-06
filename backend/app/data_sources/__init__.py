"""Market data source abstraction layer.

This package provides normalized OHLCV data in a consistent schema:
{
    "timestamp": [],
    "open": [],
    "high": [],
    "low": [],
    "close": [],
    "volume": [],
}
"""

from .mock_data import MockDataSource
from .yahoo import YahooDataSource
from .tradingview import TradingViewDataSource
from .factory import get_data_source

__all__ = [
    "MockDataSource",
    "YahooDataSource",
    "TradingViewDataSource",
    "get_data_source",
]
