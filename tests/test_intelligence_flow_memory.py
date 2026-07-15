from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_intelligence_flow_memory():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )


    report = flow.create_report(consensus)


    assert report.decision is not None

    assert flow.decision_memory.count() == 1

    record = flow.decision_memory.get_latest()


    assert record.symbol == "BTCUSDT"

    assert record.action == report.decision.action

    assert record.validation_status in [
        "APPROVED",
        "REJECTED"
    ]