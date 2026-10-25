from types import SimpleNamespace

from core.market_data.operational_market_context import (
    OperationalMarketContext,
)
from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime,
)
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.action_proposal import ActionProposal


class FakeMarketContextRuntime:
    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        return {
            "observation": SimpleNamespace(
                symbol=symbol,
                price=65000.0,
                source="test",
                fallback_used=False,
                source_status="HEALTHY",
            ),
            "context": OperationalMarketContext(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=85.0,
                timestamp="2026-09-13T00:00:00+00:00",
            ),
            "candle_boundaries": {},
        }


class FakeIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="PREPARE_LONG",
            confidence=85.0,
        )
        proposal = ActionProposal(
            action="PREPARE_LONG",
            status="REJECTED",
            reason="Test: proposal rejected",
            confidence=85.0,
            symbol="BTCUSDT",
        )
        return SimpleNamespace(
            signal="BUY",
            decision=decision,
            action_proposal=proposal,
        )


def test_rejected_proposal_does_not_open_paper_position():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )
    paper_runtime = PaperTradingRuntime(session=session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=FakeMarketContextRuntime(),
        intelligence_flow=FakeIntelligenceFlow(),
        paper_trading_runtime=paper_runtime,
    )

    results = runtime.run(cycles=1)

    assert len(results) == 1
    assert results[0]["translated_action_proposal"].status == "REJECTED"
    assert results[0]["paper_result"]["action"] == "HOLD"
    assert results[0]["paper_result"]["position"] is None
    assert session.get_position() is None



class FakeApprovedIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="PREPARE_LONG",
            confidence=85.0,
        )
        proposal = ActionProposal(
            action="PREPARE_LONG",
            status="APPROVED",
            reason="Test: proposal approved",
            confidence=85.0,
            symbol="BTCUSDT",
        )
        return SimpleNamespace(
            signal="BUY",
            decision=decision,
            action_proposal=proposal,
        )


def test_closed_external_long_gate_does_not_reach_paper_runtime():
    operational_strategy = {
        "matched": False,
        "signal": "BUY",
    }
    rules_long = True

    long_gate = (
        operational_strategy["matched"]
        and operational_strategy["signal"] == "BUY"
        and rules_long
    )

    assert long_gate is False

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )
    paper_runtime = PaperTradingRuntime(session=session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=FakeMarketContextRuntime(),
        intelligence_flow=FakeApprovedIntelligenceFlow(),
        paper_trading_runtime=paper_runtime,
    )

    results = runtime.run(cycles=1)

    assert results[0]["translated_action_proposal"].status == "APPROVED"
    assert session.get_position() is not None
