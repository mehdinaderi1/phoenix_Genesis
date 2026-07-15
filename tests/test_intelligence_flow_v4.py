from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow


def test_intelligence_flow_v4():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()

    report = flow.create_report(
        consensus
    )

    assert report.decision.action == "PREPARE_LONG"
    assert report.decision.confidence == 85