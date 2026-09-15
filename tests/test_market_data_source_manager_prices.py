from core.market_data.source_manager import MarketDataSourceManager


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def connect(self):
        return True

    def get_price(self, symbol):
        return self.price


def test_manager_returns_prices_from_all_healthy_sources():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(65020.0),
    })

    prices = manager.get_prices("BTCUSDT")

    assert prices == {
        "binance": 65000.0,
        "coinmarketcap": 65020.0,
    }


def test_manager_skips_unhealthy_sources():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(65020.0, healthy=False),
    })

    prices = manager.get_prices("BTCUSDT")

    assert prices == {
        "binance": 65000.0,
    }


def test_manager_returns_empty_when_all_sources_are_unhealthy():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0, healthy=False),
        "coinmarketcap": FakeSource(65020.0, healthy=False),
    })

    prices = manager.get_prices("BTCUSDT")

    assert prices == {}
