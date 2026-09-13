from abc import ABC, abstractmethod


class MarketDataSource(ABC):
    """Common contract for Phoenix Genesis market-data sources."""

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_price(self, symbol):
        pass

    @abstractmethod
    def get_candle(self, symbol, timeframe="1m"):
        pass

    @abstractmethod
    def get_historical_candles(self, symbol, timeframe="1m", limit=30):
        pass

    def health_check(self):
        try:
            self.connect()
            return True
        except Exception:
            return False
