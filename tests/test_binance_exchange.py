from exchanges.binance_exchange import BinanceExchange


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        import json
        return json.dumps(self.payload).encode("utf-8")


def test_binance_exchange_connects(monkeypatch):
    exchange = BinanceExchange()

    def fake_urlopen(request, timeout):
        assert request.full_url.endswith("/api/v3/ping")
        return FakeResponse({})

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen
    )

    assert exchange.connect() == "Binance Connected"
    assert exchange.connected is True


def test_binance_exchange_returns_price(monkeypatch):
    exchange = BinanceExchange()

    def fake_urlopen(request, timeout):
        assert "symbol=BTCUSDT" in request.full_url
        return FakeResponse({"symbol": "BTCUSDT", "price": "65000.25"})

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen
    )

    assert exchange.get_price("BTCUSDT") == 65000.25


def test_binance_exchange_returns_candle(monkeypatch):
    exchange = BinanceExchange()

    candle = [
        1752364800000,
        "64950.0",
        "65100.0",
        "64800.0",
        "65000.0",
        "125.5",
        1752364859999,
        "8150000.0",
        42,
        "60.0",
        "3900000.0",
        "0"
    ]

    def fake_urlopen(request, timeout):
        assert "symbol=BTCUSDT" in request.full_url
        assert "interval=1m" in request.full_url
        return FakeResponse([candle])

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen
    )

    result = exchange.get_candle("BTCUSDT", "1m")

    assert result["timestamp"] == 1752364800
    assert result["open"] == 64950.0
    assert result["high"] == 65100.0
    assert result["low"] == 64800.0
    assert result["close"] == 65000.0
    assert result["volume"] == 125.5


def test_binance_exchange_returns_historical_candles(monkeypatch):
    exchange = BinanceExchange()

    candles = [
        [
            1752364800000,
            "64950",
            "65100",
            "64800",
            "65000",
            "125.5"
        ],
        [
            1752364860000,
            "65450",
            "65600",
            "65300",
            "65500",
            "130.0"
        ]
    ]

    def fake_urlopen(request, timeout):
        assert "symbol=BTCUSDT" in request.full_url
        assert "interval=1m" in request.full_url
        assert "limit=2" in request.full_url
        return FakeResponse(candles)

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen
    )

    result = exchange.get_historical_candles(
        "BTCUSDT",
        "1m",
        2
    )

    assert len(result) == 2
    assert result[0]["close"] == 65000.0
    assert result[1]["close"] == 65500.0
