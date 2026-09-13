from core.market_data.observer import RealMarketObserver
from core.market_data.observer_runtime import RealMarketObserverRuntime
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


def test_observer_runtime_runs_multiple_observations(capsys):
    source = SequenceSource([65000.0, 65500.0, 66000.0])
    manager = MarketDataSourceManager({"binance": source})
    observer = RealMarketObserver(manager)
    runtime = RealMarketObserverRuntime(observer)

    observations = runtime.run("BTCUSDT", cycles=3)

    assert len(observations) == 3
    assert [item.price for item in observations] == [65000.0, 65500.0, 66000.0]
    assert [item.observation_number for item in observations] == [1, 2, 3]

    output = capsys.readouterr().out
    assert "[OBSERVE] BTCUSDT #1" in output
    assert "[OBSERVE] BTCUSDT #2" in output
    assert "[OBSERVE] BTCUSDT #3" in output
    assert "price=65000.0" in output
    assert "price=66000.0" in output


def test_observer_runtime_rejects_invalid_cycles():
    source = SequenceSource([65000.0])
    manager = MarketDataSourceManager({"binance": source})
    observer = RealMarketObserver(manager)
    runtime = RealMarketObserverRuntime(observer)

    try:
        runtime.run("BTCUSDT", cycles=0)
        assert False
    except ValueError as exc:
        assert str(exc) == "cycles must be greater than zero"
