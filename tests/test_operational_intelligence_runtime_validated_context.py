from core.database import DatabaseManager
from core.market_data.cross_source_validator import CrossSourceValidationResult
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.market_data.validated_market_context import ValidatedMarketContext


class FakeMarketContextRuntime:
    def __init__(self):
        self.calls = 0

    def run(self, symbol="BTCUSDT", cycles=1):
        self.calls += 1

        validation = CrossSourceValidationResult(
            status="VALID",
            primary_source="binance",
            reference_source="coinmarketcap",
            price=65000.0,
            difference_percent=0.03,
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-01-01T00:00:00+00:00",
        )

        return [
            ValidatedMarketContext(
                context=context,
                validation=validation,
            )
        ]


class FakeReport:
    decision = "BUY"
    action_proposal = "WAIT"


class FakeIntelligenceFlow:
    def __init__(self):
        self.calls = 0
        self.consensus = None

    def create_report(self, consensus):
        self.calls += 1
        self.consensus = consensus
        return FakeReport()


def test_operational_intelligence_runtime_accepts_validated_market_context(
    tmp_path
):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    market_context_runtime = FakeMarketContextRuntime()
    intelligence_flow = FakeIntelligenceFlow()

    runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=intelligence_flow,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert market_context_runtime.calls == 1
    assert intelligence_flow.calls == 1

    assert len(results) == 1
    assert isinstance(results[0]["market_context"], ValidatedMarketContext)
    assert results[0]["market_context"].validation.status == "VALID"

    assert results[0]["intelligence_context"].symbol == "BTCUSDT"
    assert results[0]["intelligence_context"].trend == "BULLISH"
    assert results[0]["intelligence_context"].signal == "BUY"
    assert results[0]["intelligence_context"].confidence == 85.0

    assert results[0]["decision"] == "BUY"
    assert results[0]["action_proposal"] == "WAIT"

    database.close()
