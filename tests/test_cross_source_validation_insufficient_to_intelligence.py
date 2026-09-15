from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.source_manager import MarketDataSourceManager


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def connect(self):
        return True

    def get_price(self, symbol):
        return self.price


class FakeMarketContext:
    symbol = "BTCUSDT"
    trend = "BULLISH"
    signal = "BUY"
    confidence = 85.0
    timestamp = "2026-01-01T00:00:00+00:00"


class RecordingContextPipeline:
    def __init__(self):
        self.calls = 0

    def build(self, symbol):
        self.calls += 1
        return FakeMarketContext()


class RecordingIntelligenceFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        assert consensus.trend == "BULLISH"
        assert consensus.signal == "BUY"
        assert consensus.confidence == 85.0

        return type(
            "Report",
            (),
            {
                "decision": "BUY",
                "action_proposal": "WAIT",
            },
        )()


def test_insufficient_cross_source_data_reaches_intelligence(tmp_path):
    database = DatabaseManager(
        db_path=str(tmp_path / "phoenix.db")
    )
    database.connect()

    manager = MarketDataSourceManager(
        {
            "binance": FakeSource(65000.0),
            "coinmarketcap": FakeSource(
                65020.0,
                healthy=False,
            ),
        }
    )

    validator = CrossSourceValidator(
        max_difference_percent=1.0
    )

    validation_pipeline = CrossSourceValidationPipeline(
        manager,
        validator,
    )

    market_runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=validation_pipeline,
    )

    context_pipeline = RecordingContextPipeline()
    market_runtime.context_pipeline = context_pipeline

    intelligence = RecordingIntelligenceFlow()

    runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(results) == 1
    assert validation_pipeline.validate("BTCUSDT").status == "INSUFFICIENT"
    assert context_pipeline.calls == 1
    assert intelligence.calls == 1
    assert results[0]["decision"] == "BUY"

    database.close()
