from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class LongRunningMarketRuntime:
    def __init__(self):
        self.calls = 0
        self.prices = [
            65000.0,
            65500.0,
            66000.0,
            66000.0,
            65500.0,
            65000.0,
        ]

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
            timestamp=f"2026-09-13T00:00:{self.calls:02d}+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


class LongRunningIntelligenceFlow:
    def __init__(self):
        self.real_flow = IntelligenceFlow()
        self.real_flow.enable_inline_outcome_learning = False
        self.calls = 0

        self.decision_outcome_bridge = (
            self.real_flow.decision_outcome_bridge
        )

    def create_report(self, consensus):
        report = self.real_flow.create_report(consensus)

        actions = (
            "PREPARE_LONG",
            "WAIT",
            "PREPARE_SHORT",
            "PREPARE_SHORT",
            "WAIT",
            "PREPARE_LONG",
        )

        action = actions[self.calls]
        self.calls += 1

        report.decision.action = action
        report.decision.strategy = {
            "name": f"LONG_RUNNING_STRATEGY_{self.calls}"
        }

        report.action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason=f"Long-running action: {action}",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=report.decision.strategy,
            risk_status="LOW",
            metadata={}
        )

        return report


def test_operational_paper_runtime_remains_stable_across_multiple_trades():
    market_runtime = LongRunningMarketRuntime()
    intelligence = LongRunningIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=intelligence.decision_outcome_bridge
    )

    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(cycles=6)

    assert len(results) == 6
    assert market_runtime.calls == 6
    assert intelligence.calls == 6

    assert [
        result["paper_result"]["action"]
        for result in results
    ] == [
        "OPEN",
        "HOLD",
        "CLOSE",
        "OPEN",
        "HOLD",
        "CLOSE",
    ]

    assert results[2]["paper_result"]["learning_result"] is not None
    assert results[5]["paper_result"]["learning_result"] is not None

    experiences = (
        intelligence.real_flow.experience_memory.experiences
    )

    assert len(experiences) == 2
    assert all(experience.success for experience in experiences)

    assert session.get_position() is None
    assert session.get_trade_count() == 2
    assert session.get_total_pnl() > 0

    summary = runtime.build_summary(results)

    assert summary["cycles_processed"] == 6
    assert summary["open_count"] == 2
    assert summary["hold_count"] == 2
    assert summary["close_count"] == 2
    assert summary["current_position"] is None
    assert summary["trade_count"] == 2
    assert summary["total_pnl"] > 0
