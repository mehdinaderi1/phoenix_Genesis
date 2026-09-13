from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.source_manager import MarketDataSourceManager


class FakeHealthySource:
    def __init__(self, price):
        self.price = price
        self.calls = 0

    def health_check(self):
        return True

    def get_price(self, symbol):
        self.calls += 1
        return self.price


class FakeFailingSource:
    def __init__(self):
        self.calls = 0

    def health_check(self):
        return True

    def get_price(self, symbol):
        self.calls += 1
        raise RuntimeError("source unavailable")


def test_observer_uses_primary_source():
    primary = FakeHealthySource(65000.0)
    fallback = FakeHealthySource(64000.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "coinmarketcap": fallback,
    })

    observer = RealMarketObserver(manager)
    result = observer.observe("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price == 65000.0
    assert result.source == "binance"
    assert result.fallback_used is False
    assert result.source_status == "HEALTHY"
    assert primary.calls == 1
    assert fallback.calls == 0


def test_observer_receives_fallback_from_source_manager():
    primary = FakeFailingSource()
    fallback = FakeHealthySource(65500.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "coinmarketcap": fallback,
    })

    observer = RealMarketObserver(manager)
    result = observer.observe("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price == 65500.0
    assert result.source == "coinmarketcap"
    assert result.fallback_used is True
    assert result.source_status == "HEALTHY"
    assert primary.calls == 1
    assert fallback.calls == 1
