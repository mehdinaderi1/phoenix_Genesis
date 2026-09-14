from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime
)
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange


class FakeSourceManager:
    def get_price(self, symbol):
        return MarketData(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )


def test_operational_market_context_runtime_run_cycle_returns_observation_and_context():
    database = DatabaseManager(":memory:")
    database.connect()

    exchange = MockExchange()

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [{
                "timestamp": 1001,
                "open": 65000,
                "high": 65100,
                "low": 64900,
                "close": 65000,
                "volume": 1
            }]
        )

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    market_data_pipeline = MarketDataPipeline(
        exchange_manager,
        database
    )

    observer = RealMarketObserver(FakeSourceManager())

    runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=market_data_pipeline,
        database=database
    )

    result = runtime.run_cycle()

    assert result["observation"] is not None
    assert result["observation"].price == 65000.0
    assert result["observation"].source == "mock"

    assert result["context"] is not None
    assert result["context"].symbol == "BTCUSDT"
    assert result["context"].trend is not None

    database.close()
