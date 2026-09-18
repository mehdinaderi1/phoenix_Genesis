from exchanges.xt_exchange import XTExchange
from core.market_data.source_manager import MarketDataSourceManager


def test_xt_can_be_primary_market_source():
    xt = XTExchange(timeout=5)
    manager = MarketDataSourceManager({"xt": xt})
    manager.set_primary_source("xt")

    data = manager.get_price("BTCUSDT")

    assert data is not None
    assert data.symbol == "BTCUSDT"
    assert data.source == "xt"
    assert data.price > 0
    assert data.fallback_used is False
    assert data.source_status == "HEALTHY"


def test_xt_appears_as_healthy_source():
    xt = XTExchange(timeout=5)
    manager = MarketDataSourceManager({"xt": xt})

    assert manager.get_healthy_sources() == ["xt"]
