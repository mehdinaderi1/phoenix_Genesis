from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FakeOperationalMarketContextRuntime:
    def __init__(self):
        self.calls = 0
        self.prices = [65000.0, 65500.0, 66000.0]

    def run_cycle(self, symbol="BTCUSDT"):
        price = self.prices[self.calls]
        self.calls += 1

        observation = SimpleNamespace(
            symbol=symbol,
            price=price,
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
        self.calls = 0
        self.actions = ["PREPARE_LONG", "WAIT", "PREPARE_SHORT"]

    def create_report(self, consensus):
        action = self.actions[self.calls]
        self.calls += 1

        decision = SimpleNamespace(
            action=action,
            reason="test",
            confidence=85.0
        )

        action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason="test",
            confidence=85.0,
            symbol=None,
            strategy=None,
            risk_status="LOW",
            metadata={}
        )

        return SimpleNamespace(
            decision=decision,
            action_proposal=action_proposal
        )


def test_operational_paper_runtime_runs_multiple_cycles():
    market_runtime = FakeOperationalMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(cycles=3)

    assert len(results) == 3
    assert market_runtime.calls == 3
    assert intelligence.calls == 3

    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[0]["paper_result"]["position"] is not None
    assert results[0]["paper_result"]["position"].entry_price == 65000.0

    assert results[1]["paper_result"]["action"] == "HOLD"
    assert results[1]["paper_result"]["position"] is not None

    assert results[2]["paper_result"]["action"] == "CLOSE"
    assert results[2]["paper_result"]["exit_price"] == 66000.0
    assert results[2]["paper_result"]["realized_pnl"] > 0

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0
