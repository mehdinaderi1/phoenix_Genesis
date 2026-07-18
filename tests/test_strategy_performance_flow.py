from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_strategy_performance_flow():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )


    report = flow.create_report(
        consensus
    )


    assert hasattr(
        report,
        "strategy_performance"
    )