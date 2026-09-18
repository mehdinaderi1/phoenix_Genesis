from exchanges.xt_exchange import XTExchange


def test_xt_price_and_30m_candle():
    exchange = XTExchange(timeout=5)

    assert exchange.health_check() is True

    price = exchange.get_price("BTCUSDT")
    assert isinstance(price, float)
    assert price > 0

    candle = exchange.get_candle("BTCUSDT", "30m")

    assert candle is not None
    assert set(candle) == {
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }
    assert candle["timestamp"] > 0
    assert candle["high"] >= candle["low"]


def test_xt_timeframe_validation():
    exchange = XTExchange()

    assert exchange._normalize_interval("1m") == "1m"
    assert exchange._normalize_interval("30m") == "30m"
    assert exchange._normalize_interval("4H") == "4h"
    assert exchange._normalize_interval("1D") == "1d"

    try:
        exchange._normalize_interval("5m")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported timeframe must raise ValueError")
