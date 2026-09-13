from core.market_data.market_data import MarketData
from core.market_data.observer import MarketObservation, RealMarketObserver
from core.market_data.observer_loop import RealMarketObservationLoop
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


def test_observation_loop_collects_multiple_observations():
    source = SequenceSource([65000.0, 65500.0, 66000.0])
    manager = MarketDataSourceManager({"binance": source})
    observer = RealMarketObserver(manager)
    loop = RealMarketObservationLoop(observer)

    observations = loop.run("BTCUSDT", cycles=3)

    assert len(observations) == 3
    assert [item.price for item in observations] == [65000.0, 65500.0, 66000.0]
    assert [item.observation_number for item in observations] == [1, 2, 3]
    assert all(isinstance(item, MarketObservation) for item in observations)


def test_observation_loop_rejects_invalid_cycle_count():
    source = SequenceSource([65000.0])
    manager = MarketDataSourceManager({"binance": source})
    observer = RealMarketObserver(manager)
    loop = RealMarketObservationLoop(observer)

    try:
        loop.run("BTCUSDT", cycles=0)
        assert False
    except ValueError as exc:
        assert str(exc) == "cycles must be greater than zero"
