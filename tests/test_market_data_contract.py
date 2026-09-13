from core.market_data.market_data import MarketData


def test_market_data_contract_defaults():
    data = MarketData(
        symbol="BTCUSDT",
        price=65000.0,
        source="binance"
    )

    assert data.symbol == "BTCUSDT"
    assert data.price == 65000.0
    assert data.source == "binance"
    assert data.fallback_used is False
    assert data.source_status == "HEALTHY"


def test_market_data_contract_supports_fallback():
    data = MarketData(
        symbol="BTCUSDT",
        price=65100.0,
        source="cmc",
        fallback_used=True
    )

    assert data.source == "cmc"
    assert data.fallback_used is True
