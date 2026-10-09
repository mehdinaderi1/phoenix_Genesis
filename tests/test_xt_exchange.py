from unittest.mock import patch

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
    assert exchange._normalize_interval("5m") == "5m"
    assert exchange._normalize_interval("15m") == "15m"
    assert exchange._normalize_interval("4H") == "4h"
    assert exchange._normalize_interval("1D") == "1d"

    try:
        exchange._normalize_interval("2h")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported timeframe must raise ValueError")


def test_xt_request_retries_after_transient_failure():
    exchange = XTExchange(timeout=5)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"{\"result\": {\"ok\": true}}"

    attempts = []

    def fake_urlopen(request, timeout):
        attempts.append(timeout)
        if len(attempts) < 3:
            raise OSError("temporary network failure")
        return FakeResponse()

    with patch("exchanges.xt_exchange.urllib.request.urlopen", side_effect=fake_urlopen):
        with patch("exchanges.xt_exchange.time.sleep"):
            result = exchange._request("/test")

    assert result == {"result": {"ok": True}}
    assert attempts == [5, 5, 5]
def test_xt_historical_candles_are_chronological():
    exchange = XTExchange(timeout=5)

    payload = {
        "result": [
            {"t": 3000, "o": "103", "h": "104", "l": "102", "c": "103.5", "v": "30"},
            {"t": 2000, "o": "102", "h": "103", "l": "101", "c": "102.5", "v": "20"},
            {"t": 1000, "o": "101", "h": "102", "l": "100", "c": "101.5", "v": "10"}
        ]
    }

    with patch.object(exchange, "_request", return_value=payload):
        candles = exchange.get_historical_candles("BTCUSDT", timeframe="5m", limit=3)

    assert [candle["timestamp"] for candle in candles] == [1, 2, 3]


def test_xt_request_raises_after_all_retries_fail():
    exchange = XTExchange(timeout=5)
    attempts = []
    delays = []

    def fake_urlopen(request, timeout):
        attempts.append(timeout)
        raise OSError("simulated network disconnect")

    def fake_sleep(seconds):
        delays.append(seconds)

    with patch(
        "exchanges.xt_exchange.urllib.request.urlopen",
        side_effect=fake_urlopen,
    ):
        with patch(
            "exchanges.xt_exchange.time.sleep",
            side_effect=fake_sleep,
        ):
            try:
                exchange._request("/test")
            except OSError as exc:
                assert str(exc) == "simulated network disconnect"
            else:
                raise AssertionError("Expected OSError after retries")

    assert attempts == [5, 5, 5]
    assert delays == [1, 2]
