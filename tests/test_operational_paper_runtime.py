from types import SimpleNamespace

from core.market_data.market_data import MarketData
from core.market_data.operational_market_context import (
    OperationalMarketContext
)
from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime
)


class FakeMarketContextRuntime:
    def run_cycle(self, symbol="BTCUSDT"):
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


class FakePaperTradingRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "action": "OPEN",
            "position": SimpleNamespace(
                side="BUY",
                entry_price=cycles[0]["price"]
            ),
            "realized_pnl": 0.0,
            "learning_result": None
        }]


def test_operational_paper_runtime_connects_market_intelligence_and_paper():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(cycles=2)

    assert len(results) == 2
    assert len(intelligence.consensuses) == 2
    assert len(paper_runtime.cycles) == 2

    assert paper_runtime.cycles[0]["price"] == 65000.0
    assert paper_runtime.cycles[0]["symbol"] == "BTCUSDT"
    assert paper_runtime.cycles[0]["decision"].action == "BUY"
    assert paper_runtime.cycles[0]["action_proposal"].action == "BUY"

    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[0]["paper_result"]["position"].entry_price == 65000.0


def test_operational_paper_runtime_rejects_missing_dependencies():
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    try:
        OperationalPaperRuntime(
            None,
            intelligence,
            paper_runtime
        )
    except ValueError as exc:
        assert str(exc) == "market_context_runtime must not be None"
    else:
        raise AssertionError("Expected ValueError")

    try:
        OperationalPaperRuntime(
            FakeMarketContextRuntime(),
            None,
            paper_runtime
        )
    except ValueError as exc:
        assert str(exc) == "intelligence_flow must not be None"
    else:
        raise AssertionError("Expected ValueError")

    try:
        OperationalPaperRuntime(
            FakeMarketContextRuntime(),
            intelligence,
            None
        )
    except ValueError as exc:
        assert str(exc) == "paper_trading_runtime must not be None"
    else:
        raise AssertionError("Expected ValueError")
