from core.database import DatabaseManager
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime
)
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange


class FakeObservation:
    def __init__(self, status="HEALTHY"):
        self.symbol = "BTCUSDT"
        self.price = 65012.34
        self.source = "coinmarketcap"
        self.fallback_used = False
        self.source_status = status


class FakeObserver:
    def observe(self, symbol):
        return FakeObservation()


class FailingSourceCandlePipeline:
    def fetch_and_store(self, symbol="BTCUSDT", timeframe="1m"):
        return {
            "stored": False,
            "source": None,
            "candle": None
        }


def configure_mock_exchange(exchange):
    candle = {
        "timestamp": 1001,
        "open": 65000,
        "high": 65100,
        "low": 64900,
        "close": 65000,
        "volume": 1,
    }

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [candle]
        )


def test_real_price_can_use_prototype_candle_when_real_candle_unavailable():
    database = DatabaseManager(":memory:")
    database.connect()

    mock_exchange = MockExchange()
    configure_mock_exchange(mock_exchange)

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(mock_exchange)

    prototype_pipeline = MarketDataPipeline(
        exchange_manager,
        database
    )

    runtime = OperationalMarketContextRuntime(
        observer=FakeObserver(),
        market_data_pipeline=prototype_pipeline,
        database=database,
        source_candle_pipeline=FailingSourceCandlePipeline()
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=("30m", "4H", "1D")
    )

    assert result["observation"].price == 65012.34
    assert result["observation"].source == "coinmarketcap"
    assert result["observation"].source_status == "HEALTHY"

    assert result["context"] is not None
    assert result["context"].symbol == "BTCUSDT"
