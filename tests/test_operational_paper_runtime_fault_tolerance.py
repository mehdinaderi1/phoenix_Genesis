from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FaultyMarketRuntime:
    def __init__(self):
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        if self.calls == 2:
            raise RuntimeError("temporary market failure")

        observation = SimpleNamespace(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-09-13T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


class StableIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="WAIT",
            reason="test",
            confidence=85.0
        )

        action_proposal = SimpleNamespace(
            action="WAIT",
            status="APPROVED",
            reason="test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=None,
            risk_status="LOW",
            metadata={}
        )

        return SimpleNamespace(
            decision=decision,
            action_proposal=action_proposal
        )


def test_operational_paper_runtime_can_continue_after_cycle_error():
    market_runtime = FaultyMarketRuntime()
    intelligence = StableIntelligenceFlow()
    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(
        cycles=3,
        continue_on_error=True
    )

    assert market_runtime.calls == 3
    assert len(results) == 3

    assert results[0]["paper_result"]["action"] == "HOLD"
    assert results[1]["paper_result"] is None
    assert results[2]["paper_result"]["action"] == "HOLD"

    assert results[0]["cycle_number"] == 1
    assert results[1]["cycle_number"] == 2
    assert results[2]["cycle_number"] == 3

    assert results[0]["error"] is None
    assert isinstance(results[1]["error"], RuntimeError)
    assert str(results[1]["error"]) == "temporary market failure"
    assert results[2]["error"] is None
def test_operational_paper_runtime_stops_on_error_by_default():
    market_runtime = FaultyMarketRuntime()
    intelligence = StableIntelligenceFlow()
    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    try:
        runtime.run(cycles=3)
    except RuntimeError as exc:
        assert str(exc) == "temporary market failure"
    else:
        raise AssertionError("RuntimeError was expected")

    assert market_runtime.calls == 2
