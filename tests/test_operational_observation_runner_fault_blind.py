from types import SimpleNamespace

from core.market_data.operational_observation_runner import OperationalObservationRunner
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.operational_market_context import OperationalMarketContext
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FakeIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="WAIT",
            reason="integration test",
            confidence=85.0
        )
        action_proposal = SimpleNamespace(
            action="WAIT",
            status="APPROVED",
            reason="integration test",
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


class FakeMarketContextRuntime:
    def __init__(self, mode="healthy", fault_cycle=None):
        self.mode = mode
        self.fault_cycle = fault_cycle
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        if self.fault_cycle == self.calls:
            raise RuntimeError("simulated market runtime failure")

        if self.mode == "blind":
            observation = SimpleNamespace(
                symbol=symbol,
                price=None,
                source=None,
                fallback_used=False,
                source_status="BLIND"
            )
            return {
                "observation": observation,
                "context": None
            }

        observation = SimpleNamespace(
            symbol=symbol,
            price=65000.0 + self.calls * 100.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )
        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="WAIT",
            confidence=85.0,
            timestamp="2026-09-15T00:00:00+00:00"
        )
        return {
            "observation": observation,
            "context": context
        }


def build_operational_runtime(market_runtime):
    intelligence = FakeIntelligenceFlow()
    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime
    )

    return runtime, session


def test_runner_preserves_fault_tolerance():
    market_runtime = FakeMarketContextRuntime(fault_cycle=2)
    operational_runtime, session = build_operational_runtime(market_runtime)

    sleeps = []
    runner = OperationalObservationRunner(
        runtime=operational_runtime,
        sleep_fn=sleeps.append
    )

    results = runner.run(
        symbol="BTCUSDT",
        cycles=3,
        interval_seconds=5,
        continue_on_error=True
    )

    assert len(results) == 3
    assert market_runtime.calls == 3
    assert results[0]["error"] is None
    assert isinstance(results[1]["error"], RuntimeError)
    assert results[2]["error"] is None
    assert results[0]["paper_result"]["action"] == "HOLD"
    assert results[1]["paper_result"] is None
    assert results[2]["paper_result"]["action"] == "HOLD"
    assert session.get_position() is None
    assert sleeps == [5, 5]


def test_runner_preserves_blind_behavior():
    market_runtime = FakeMarketContextRuntime(mode="blind")
    operational_runtime, session = build_operational_runtime(market_runtime)

    sleeps = []
    runner = OperationalObservationRunner(
        runtime=operational_runtime,
        sleep_fn=sleeps.append
    )

    results = runner.run(
        symbol="BTCUSDT",
        cycles=3,
        interval_seconds=5
    )

    assert len(results) == 3
    assert market_runtime.calls == 3
    assert all(result["observation"].source_status == "BLIND" for result in results)
    assert all(result["market_context"] is None for result in results)
    assert all(result["paper_result"] is None for result in results)
    assert session.get_position() is None
    assert sleeps == [5, 5]
