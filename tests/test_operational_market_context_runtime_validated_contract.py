from core.database import DatabaseManager
from core.market_data.cross_source_validator import CrossSourceValidationResult
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.validated_market_context import ValidatedMarketContext


class FakeValidatedContextPipeline:
    def __init__(self):
        self.calls = 0

    def build(self, symbol):
        self.calls += 1

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-01-01T00:00:00+00:00",
        )

        validation = CrossSourceValidationResult(
            status="VALID",
            primary_source="binance",
            reference_source="coinmarketcap",
            price=65000.0,
            difference_percent=0.03,
        )

        return {
            "validation": validation,
            "context": ValidatedMarketContext(
                context=context,
                validation=validation,
            ),
        }


def test_runtime_can_use_validated_market_context_pipeline(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    pipeline = FakeValidatedContextPipeline()

    runtime = OperationalMarketContextRuntime(
        database=database,
        validated_context_pipeline=pipeline,
    )

    result = runtime.run_cycle("BTCUSDT")

    assert pipeline.calls == 1
    assert isinstance(result["context"], ValidatedMarketContext)
    assert result["context"].symbol == "BTCUSDT"
    assert result["context"].trend == "BULLISH"
    assert result["context"].signal == "BUY"
    assert result["context"].validation.status == "VALID"

    database.close()
