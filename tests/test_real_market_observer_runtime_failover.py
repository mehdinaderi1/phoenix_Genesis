from core.market_data.observer import RealMarketObserver
from core.market_data.observer_runtime import RealMarketObserverRuntime
from core.market_data.source_manager import MarketDataSourceManager


class ControlledSource:
    def __init__(self, price=None, healthy=True, failing=False):
        self.price = price
        self.healthy = healthy
        self.failing = failing

    def health_check(self):
        return self.healthy

    def get_price(self, symbol):
        if self.failing:
            raise RuntimeError("source unavailable")
        return self.price


def test_runtime_uses_primary_then_fallback(capsys):
    primary = ControlledSource(price=65000.0)
    fallback = ControlledSource(price=64500.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "coinmarketcap": fallback,
    })

    observer = RealMarketObserver(manager)
    runtime = RealMarketObserverRuntime(observer)

    first = runtime.run("BTCUSDT", cycles=1)
    assert first[0].price == 65000.0
    assert first[0].source == "binance"
    assert first[0].fallback_used is False

    primary.healthy = False

    second = runtime.run("BTCUSDT", cycles=1)
    assert second[0].price == 64500.0
    assert second[0].source == "coinmarketcap"
    assert second[0].fallback_used is True

    output = capsys.readouterr().out
    assert "source=binance" in output
    assert "source=coinmarketcap" in output


def test_runtime_reports_blind_when_all_sources_are_unavailable(capsys):
    primary = ControlledSource(healthy=False)
    fallback = ControlledSource(healthy=False)

    manager = MarketDataSourceManager({
        "binance": primary,
        "coinmarketcap": fallback,
    })

    observer = RealMarketObserver(manager)
    runtime = RealMarketObserverRuntime(observer)

    observations = runtime.run("BTCUSDT", cycles=1)

    assert len(observations) == 1
    assert observations[0].price is None
    assert observations[0].source is None
    assert observations[0].fallback_used is False
    assert observations[0].source_status == "BLIND"

    output = capsys.readouterr().out
    assert "source=NONE" in output
    assert "status=BLIND" in output
