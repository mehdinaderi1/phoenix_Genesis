from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context import (
    OperationalIntelligenceContext
)
from intelligence.flow import IntelligenceFlow


def test_operational_context_reaches_intelligence_flow():
    adapter = OperationalIntelligenceAdapter()
    intelligence = IntelligenceFlow()

    bullish_context = OperationalIntelligenceContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=85.0
    )

    bearish_context = OperationalIntelligenceContext(
        symbol="BTCUSDT",
        trend="BEARISH",
        signal="SELL",
        confidence=35.0
    )

    bullish_report = intelligence.create_report(
        adapter.to_consensus(bullish_context)
    )

    bearish_report = intelligence.create_report(
        adapter.to_consensus(bearish_context)
    )

    assert bullish_report.trend == "BULLISH"
    assert bullish_report.signal == "BUY"

    assert bearish_report.trend == "BEARISH"
    assert bearish_report.signal == "SELL"

    assert bullish_report.confidence != bearish_report.confidence


def test_operational_context_reaches_decision_layer():
    adapter = OperationalIntelligenceAdapter()
    intelligence = IntelligenceFlow()

    context = OperationalIntelligenceContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=85.0
    )

    report = intelligence.create_report(
        adapter.to_consensus(context)
    )

    assert report.decision is not None
    assert hasattr(report.decision, "action")
    assert report.action_proposal is not None
    assert report.action_proposal.action == report.decision.action
