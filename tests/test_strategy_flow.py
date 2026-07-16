from intelligence.flow import IntelligenceFlow
from tests.test_consensus import ConsensusResult


def test_strategy_flow():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(

        trend="BULLISH",

        signal="BUY",

        confidence=85

    )


    report = flow.create_report(
        consensus
    )


    assert report is not None

    assert hasattr(
        report,
        "strategy_insight"
    )


    assert report.strategy_insight is not None


    assert report.strategy_insight["score"] > 0