import json

from core.market_data.source_manager import MarketDataSourceManager
from exchanges.binance_exchange import BinanceExchange
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


def test_binance_and_cmc_integrate_with_source_manager(monkeypatch):
    def fake_urlopen(request, timeout):
        if "binance" in request.full_url.lower():
            return FakeResponse({"price": "65000.0"})

        return FakeResponse({
            "data": {
                "BTC": {
                    "quote": {
                        "USD": {
                            "price": 65100.0
                        }
                    }
                }
            }
        })

    binance = BinanceExchange()
    cmc = CoinMarketCapSource()

    binance.health_check = lambda: True
    binance.get_price = lambda symbol: 65000.0

    cmc.health_check = lambda: True
    cmc.get_price = lambda symbol: 65100.0

    manager = MarketDataSourceManager({
        "binance": binance,
        "cmc": cmc,
    })

    result = manager.get_price("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price == 65000.0
    assert result.source == "binance"
    assert result.fallback_used is False
    assert result.source_status == "HEALTHY"


def test_binance_failure_activates_cmc_fallback():
    binance = BinanceExchange()
    cmc = CoinMarketCapSource()

    binance.health_check = lambda: False
    binance.get_price = lambda symbol: 65000.0

    cmc.health_check = lambda: True
    cmc.get_price = lambda symbol: 65100.0

    manager = MarketDataSourceManager({
        "binance": binance,
        "cmc": cmc,
    })

    result = manager.get_price("BTCUSDT")

    assert result.symbol == "BTCUSDT"
    assert result.price == 65100.0
    assert result.source == "cmc"
    assert result.fallback_used is True
    assert result.source_status == "HEALTHY"
