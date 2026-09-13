import pytest

from core.market_data.source_manager import MarketDataSourceManager


class FakeSource:
    def __init__(self, price=65000.0, healthy=True):
        self.price = price
        self.healthy = healthy
        self.health_calls = 0
        self.price_calls = 0

    def health_check(self):
        self.health_calls += 1
        return self.healthy

    def get_price(self, symbol):
        self.price_calls += 1
        return self.price


class FailingSource(FakeSource):
    def get_price(self, symbol):
        self.price_calls += 1
        raise RuntimeError("source unavailable")


def test_manager_uses_primary_source():
    primary = FakeSource(price=65000.0)
    fallback = FakeSource(price=65100.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "cmc": fallback,
    })

    result = manager.get_price("BTCUSDT")

    assert result.price == 65000.0
    assert result.source == "binance"
    assert result.fallback_used is False
    assert primary.price_calls == 1
    assert fallback.price_calls == 0


def test_manager_falls_back_when_primary_is_unhealthy():
    primary = FakeSource(price=65000.0, healthy=False)
    fallback = FakeSource(price=65100.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "cmc": fallback,
    })

    result = manager.get_price("BTCUSDT")

    assert result.price == 65100.0
    assert result.source == "cmc"
    assert result.fallback_used is True
    assert primary.price_calls == 0
    assert fallback.price_calls == 1


def test_manager_falls_back_when_primary_request_fails():
    primary = FailingSource()
    fallback = FakeSource(price=65100.0)

    manager = MarketDataSourceManager({
        "binance": primary,
        "cmc": fallback,
    })

    result = manager.get_price("BTCUSDT")

    assert result.price == 65100.0
    assert result.source == "cmc"
    assert result.fallback_used is True


def test_manager_reports_no_source_when_all_are_unhealthy():
    primary = FakeSource(healthy=False)
    fallback = FakeSource(healthy=False)

    manager = MarketDataSourceManager({
        "binance": primary,
        "cmc": fallback,
    })

    with pytest.raises(RuntimeError, match="No healthy market-data source"):
        manager.get_price("BTCUSDT")


def test_manager_can_change_primary_source():
    binance = FakeSource(price=65000.0)
    cmc = FakeSource(price=65100.0)

    manager = MarketDataSourceManager({
        "binance": binance,
        "cmc": cmc,
    })

    manager.set_primary_source("cmc")

    result = manager.get_price("BTCUSDT")

    assert result.source == "cmc"
    assert result.price == 65100.0


def test_manager_rejects_unknown_primary_source():
    manager = MarketDataSourceManager({
        "binance": FakeSource()
    })

    with pytest.raises(ValueError, match="Unknown market-data source"):
        manager.set_primary_source("unknown")


def test_manager_lists_healthy_sources():
    healthy = FakeSource()
    unhealthy = FakeSource(healthy=False)

    manager = MarketDataSourceManager({
        "binance": healthy,
        "cmc": unhealthy,
    })

    assert manager.get_healthy_sources() == ["binance"]
