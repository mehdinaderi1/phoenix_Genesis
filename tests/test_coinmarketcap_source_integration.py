import json

from core.market_data.observer import RealMarketObserver
from core.market_data.source_manager import MarketDataSourceManager
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


def test_coinmarketcap_flows_through_source_manager_and_observer(monkeypatch):
    payload = {
        "data": [
            {
                "id": 1,
                "symbol": "BTC",
                "quote": [
                    {
                        "symbol": "USD",
                        "price": 65012.34
                    }
                ]
            }
        ]
    }

    def fake_urlopen(request, timeout):
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    cmc = CoinMarketCapSource()
    manager = MarketDataSourceManager({"coinmarketcap": cmc})
    observer = RealMarketObserver(manager)

    observation = observer.observe("BTCUSDT")

    assert observation.symbol == "BTCUSDT"
    assert observation.price == 65012.34
    assert observation.source == "coinmarketcap"
    assert observation.fallback_used is False
    assert observation.source_status == "HEALTHY"
    assert observation.observation_number == 1
