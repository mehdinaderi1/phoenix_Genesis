from types import SimpleNamespace

from core.market_data.operational_intelligence_runtime import (
    OperationalIntelligenceRuntime
)
from core.market_data.operational_market_context import (
    OperationalMarketContext
)


class FakeMarketContextRuntime:
    def run(self, symbol="BTCUSDT", cycles=1):
        return [
            OperationalMarketContext(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=85.0,
                timestamp="2026-09-13T00:00:00+00:00"
            )
            for _ in range(cycles)
        ]


class FakeIntelligenceFlow:
    def __init__(self):
        self.consensuses = []

    def create_report(self, consensus):
        self.consensuses.append(consensus)
        decision = SimpleNamespace(action="BUY")
        proposal = SimpleNamespace(action="BUY")
        return SimpleNamespace(
            decision=decision,
            action_proposal=proposal
        )


def test_operational_intelligence_runtime_connects_context_to_intelligence():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()

    runtime = OperationalIntelligenceRuntime(
        market_runtime,
        intelligence
    )

    results = runtime.run(cycles=2)

    assert len(results) == 2
    assert len(intelligence.consensuses) == 2

    assert intelligence.consensuses[0].trend == "BULLISH"
    assert intelligence.consensuses[0].signal == "BUY"
    assert intelligence.consensuses[0].confidence == 85.0

    assert results[0]["market_context"].trend == "BULLISH"
    assert results[0]["intelligence_context"].trend == "BULLISH"
    assert results[0]["report"].decision.action == "BUY"
    assert results[0]["action_proposal"].action == "BUY"


def test_operational_intelligence_runtime_rejects_missing_dependencies():
    intelligence = FakeIntelligenceFlow()

    try:
        OperationalIntelligenceRuntime(None, intelligence)
    except ValueError as exc:
        assert str(exc) == "market_context_runtime must not be None"
    else:
        raise AssertionError("Expected ValueError")

    try:
        OperationalIntelligenceRuntime(
            FakeMarketContextRuntime(),
            None
        )
    except ValueError as exc:
        assert str(exc) == "intelligence_flow must not be None"
    else:
        raise AssertionError("Expected ValueError")
