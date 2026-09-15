from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.validated_market_context_pipeline import ValidatedMarketContextPipeline


class FakeSource:
    def __init__(self, price):
        self.price = price

    def health_check(self):
        return True

    def get_price(self, symbol):
        return self.price


class RecordingContextPipeline:
    def __init__(self, database):
        self.database = database

    def build(self, symbol):
        from core.market_data.operational_market_context import OperationalMarketContext

        return OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-01-01T00:00:00+00:00",
        )


class RecordingIntelligenceFlow:
    def __init__(self):
        self.calls = []

    def create_report(self, consensus):
        self.calls.append(consensus)

        from types import SimpleNamespace

        return SimpleNamespace(
            decision="BUY",
            action_proposal="WAIT",
        )


def test_validated_context_feeds_operational_intelligence(tmp_path):
    database = DatabaseManager(
        db_path=str(tmp_path / "phoenix.db")
    )
    database.connect()

    manager = MarketDataSourceManager(
        {
            "binance": FakeSource(65000.0),
            "coinmarketcap": FakeSource(65020.0),
        }
    )

    validation_pipeline = CrossSourceValidationPipeline(manager)

    validated_pipeline = ValidatedMarketContextPipeline(
        database=database,
        validation_pipeline=validation_pipeline,
    )

    validated_pipeline.context_pipeline = RecordingContextPipeline(database)

    result = validated_pipeline.build("BTCUSDT")

    assert result["validation"].status == "VALID"
    assert result["context"] is not None
    assert result["context"].validation.status == "VALID"

    runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=validation_pipeline,
    )

    runtime.context_pipeline = validated_pipeline.context_pipeline

    intelligence = RecordingIntelligenceFlow()

    from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime

    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=runtime,
        intelligence_flow=intelligence,
    )

    results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(results) == 1
    assert len(intelligence.calls) == 1
    assert intelligence.calls[0].trend == "BULLISH"
    assert intelligence.calls[0].signal == "BUY"
    assert intelligence.calls[0].confidence == 85.0
    assert results[0]["decision"] == "BUY"

    database.close()
