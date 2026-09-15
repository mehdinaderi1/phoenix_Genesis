from core.database import DatabaseManager
from core.market_data.cross_source_validator import CrossSourceValidationResult
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.market_data.validated_market_context import ValidatedMarketContext
from intelligence.flow import IntelligenceFlow


class RealValidatedMarketContextRuntime:
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


def test_validated_market_context_reaches_real_intelligence_flow(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    market_context_runtime = RealValidatedMarketContextRuntime()
    intelligence_flow = IntelligenceFlow()

    runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=intelligence_flow,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert market_context_runtime.calls == 1
    assert len(results) == 1

    result = results[0]

    assert isinstance(result["market_context"], ValidatedMarketContext)
    assert result["market_context"].validation.status == "VALID"

    assert result["intelligence_context"].symbol == "BTCUSDT"
    assert result["intelligence_context"].trend == "BULLISH"
    assert result["intelligence_context"].signal == "BUY"
    assert result["intelligence_context"].confidence == 85.0

    assert result["report"] is not None
    assert result["decision"] is not None
    assert result["action_proposal"] is not None

    database.close()
