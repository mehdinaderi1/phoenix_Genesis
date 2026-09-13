import json

import pytest

from exchanges.coinmarketcap_source import CoinMarketCapSource


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_coinmarketcap_get_price(monkeypatch):
    payload = {
        "data": {
            "BTC": {
                "quote": {
                    "USD": {
                        "price": 65012.34
                    }
                }
            }
        }
    }

    def fake_urlopen(request, timeout):
        assert "quotes/latest" in request.full_url
        assert "symbol=BTC" in request.full_url
        assert "convert=USD" in request.full_url
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    source = CoinMarketCapSource()

    assert source.get_price("BTCUSDT") == pytest.approx(65012.34)


def test_coinmarketcap_connect(monkeypatch):
    payload = {
        "data": {
            "BTC": {
                "quote": {
                    "USD": {
                        "price": 65000.0
                    }
                }
            }
        }
    }

    def fake_urlopen(request, timeout):
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    source = CoinMarketCapSource()

    assert source.connect() == "CoinMarketCap Connected"
    assert source.connected is True


def test_coinmarketcap_rejects_unknown_symbol():
    source = CoinMarketCapSource()

    with pytest.raises(ValueError):
        source.get_price("UNKNOWNUSDT")


def test_coinmarketcap_candle_is_explicitly_unsupported():
    source = CoinMarketCapSource()

    with pytest.raises(NotImplementedError):
        source.get_candle("BTCUSDT", "1m")
