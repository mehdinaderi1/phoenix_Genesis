from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.source_manager import MarketDataSourceManager


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def connect(self):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return True

    def get_price(self, symbol):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return self.price


class PrototypeComposition:
    """Minimal composition root for multi-source observation."""

    def __init__(self, primary, fallback):
        self.source_manager = MarketDataSourceManager({
            "primary": primary,
            "fallback": fallback,
        })
        self.source_manager.set_primary_source("primary")
        self.observer = RealMarketObserver(self.source_manager)


def test_composition_uses_primary_source():
    primary = FakeSource(65000.0, healthy=True)
    fallback = FakeSource(64000.0, healthy=True)

    composition = PrototypeComposition(primary, fallback)

    observation = composition.observer.observe("BTCUSDT")

    assert observation.source == "primary"
    assert observation.price == 65000.0
    assert observation.fallback_used is False
    assert observation.source_status == "HEALTHY"


def test_composition_uses_fallback_when_primary_fails():
    primary = FakeSource(65000.0, healthy=False)
    fallback = FakeSource(64000.0, healthy=True)

    composition = PrototypeComposition(primary, fallback)

    observation = composition.observer.observe("BTCUSDT")

    assert observation.source == "fallback"
    assert observation.price == 64000.0
    assert observation.fallback_used is True
    assert observation.source_status == "HEALTHY"


def test_composition_enters_blind_state_when_all_sources_fail():
    primary = FakeSource(65000.0, healthy=False)
    fallback = FakeSource(64000.0, healthy=False)

    composition = PrototypeComposition(primary, fallback)

    observation = composition.observer.observe("BTCUSDT")

    assert observation.source is None
    assert observation.price is None
    assert observation.fallback_used is False
    assert observation.source_status == "BLIND"
