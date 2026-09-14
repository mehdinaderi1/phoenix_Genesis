from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_intelligence_runtime import (
    OperationalIntelligenceRuntime
)
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime
)
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from intelligence.flow import IntelligenceFlow


class FakeSourceManager:
    def get_price(self, symbol):
        return MarketData(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )


def test_operational_market_context_reaches_real_intelligence():
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

    observer = RealMarketObserver(
        FakeSourceManager()
    )

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=market_data_pipeline,
        database=database
    )

    intelligence = IntelligenceFlow()
    intelligence.enable_inline_outcome_learning = False

    runtime = OperationalIntelligenceRuntime(
        market_runtime,
        intelligence
    )

    results = runtime.run(cycles=1)

    assert len(results) == 1

    result = results[0]

    assert result["market_context"].symbol == "BTCUSDT"
    assert result["intelligence_context"].symbol == "BTCUSDT"
    assert result["intelligence_context"].trend == result["market_context"].trend
    assert result["intelligence_context"].signal == result["market_context"].signal
    assert result["intelligence_context"].confidence == result["market_context"].confidence

    report = result["report"]
    assert report is not None
    assert report.decision is not None
    assert report.action_proposal is not None

    database.close()
