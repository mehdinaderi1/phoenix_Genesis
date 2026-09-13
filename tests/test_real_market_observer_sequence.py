from core.market_data.observer import RealMarketObserver
from core.market_data.source_manager import MarketDataSourceManager


class SequenceSource:
    def __init__(self, prices):
        self.prices = list(prices)
        self.index = 0

    def health_check(self):
        return True

    def get_price(self, symbol):
        price = self.prices[min(self.index, len(self.prices) - 1)]
        self.index += 1
        return price


def test_observer_records_changing_market_observations():
    source = SequenceSource([65000.0, 65500.0, 66000.0])
    manager = MarketDataSourceManager({"binance": source})
    observer = RealMarketObserver(manager)

    observations = [
        observer.observe("BTCUSDT"),
        observer.observe("BTCUSDT"),
        observer.observe("BTCUSDT"),
    ]

    assert len(observations) == 3
    assert [item.price for item in observations] == [65000.0, 65500.0, 66000.0]
    assert [item.source for item in observations] == ["binance", "binance", "binance"]
    assert [item.observation_number for item in observations] == [1, 2, 3]
    assert all(item.fallback_used is False for item in observations)
    assert all(item.source_status == "HEALTHY" for item in observations)
    assert all(item.symbol == "BTCUSDT" for item in observations)


def test_observer_preserves_fallback_across_multiple_observations():
    primary = SequenceSource([65000.0, 65500.0])
    fallback = SequenceSource([64000.0, 64500.0])

    class FailingAfterFirstSource(SequenceSource):
        def get_price(self, symbol):
            if self.index == 0:
                self.index += 1
                return self.prices[0]
            self.index += 1
            raise RuntimeError("primary source unavailable")

    primary = FailingAfterFirstSource([65000.0])
    manager = MarketDataSourceManager({
        "binance": primary,
        "coinmarketcap": fallback,
    })
    observer = RealMarketObserver(manager)

    first = observer.observe("BTCUSDT")
    second = observer.observe("BTCUSDT")

    assert first.price == 65000.0
    assert first.source == "binance"
    assert first.fallback_used is False

    assert second.price == 64000.0
    assert second.source == "coinmarketcap"
    assert second.fallback_used is True
    assert second.observation_number == 2
