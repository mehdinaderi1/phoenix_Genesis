from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver


class HealthySource:
    def health_check(self):
        return True

    def get_price(self, symbol):
        return 65000.0


class BlindSource:
    def health_check(self):
        return False

    def get_price(self, symbol):
        raise RuntimeError("unavailable")


class FakeSourceManager:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def get_price(self, symbol):
        if self.error:
            raise self.error
        return self.result


def test_real_market_observer_records_normalized_market_data():
    market_data = MarketData(
        symbol="BTCUSDT",
        price=65000.0,
        source="binance",
        fallback_used=False,
        source_status="HEALTHY",
    )

    observer = RealMarketObserver(FakeSourceManager(result=market_data))

    result = observer.observe("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price == 65000.0
    assert result.source == "binance"
    assert result.fallback_used is False
    assert result.source_status == "HEALTHY"
    assert result.observation_number == 1
    assert result.timestamp


def test_real_market_observer_increments_observation_number():
    market_data = MarketData(
        symbol="BTCUSDT",
        price=65500.0,
        source="coinmarketcap",
        fallback_used=True,
        source_status="HEALTHY",
    )

    observer = RealMarketObserver(FakeSourceManager(result=market_data))

    first = observer.observe("BTCUSDT")
    second = observer.observe("BTCUSDT")

    assert first.observation_number == 1
    assert second.observation_number == 2


def test_real_market_observer_reports_blind_when_no_source_available():
    observer = RealMarketObserver(
        FakeSourceManager(error=RuntimeError("no source available"))
    )

    result = observer.observe("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price is None
    assert result.source is None
    assert result.fallback_used is False
    assert result.source_status == "BLIND"
    assert result.observation_number == 1
    assert result.timestamp
