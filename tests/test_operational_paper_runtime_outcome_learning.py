from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class ControlledOperationalMarketRuntime:
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


class ControlledOperationalIntelligenceFlow:
    def __init__(self):
        self.real_flow = IntelligenceFlow()
        self.real_flow.enable_inline_outcome_learning = False
        self.calls = 0

        self.decision_outcome_bridge = (
            self.real_flow.decision_outcome_bridge
        )

    def create_report(self, consensus):
        report = self.real_flow.create_report(consensus)

        report.decision.action = "PREPARE_LONG"
        report.decision.strategy = {
            "name": "OPERATIONAL_PAPER_TEST_STRATEGY"
        }

        actions = ("PREPARE_LONG", "WAIT", "PREPARE_SHORT")
        action = actions[self.calls]
        self.calls += 1

        report.decision.action = action

        report.action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason=f"Controlled operational action: {action}",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=report.decision.strategy,
            risk_status="LOW",
            metadata={}
        )

        return report


def test_operational_paper_runtime_triggers_real_outcome_learning():
    market_runtime = ControlledOperationalMarketRuntime()
    intelligence = ControlledOperationalIntelligenceFlow()

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

    results = runtime.run(cycles=3)

    assert len(results) == 3
    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[1]["paper_result"]["action"] == "HOLD"
    assert results[2]["paper_result"]["action"] == "CLOSE"

    learning_result = results[2]["paper_result"]["learning_result"]

    assert learning_result is not None
    assert learning_result["performance_learning"] is not None
    assert learning_result["performance_learning"]["outcome"] == "SUCCESS"
    assert learning_result["performance_learning"]["experience"] is not None

    experiences = (
        intelligence.real_flow.experience_memory.experiences
    )

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.success is True
    assert experience.score == 100
    assert experience.strategy == "OPERATIONAL_PAPER_TEST_STRATEGY"

    summary = runtime.build_summary(results)

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 1
    assert summary["hold_count"] == 1
    assert summary["close_count"] == 1
    assert summary["current_position"] is None
    assert summary["trade_count"] == 1
    assert summary["total_pnl"] > 0
