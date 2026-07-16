from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult



def test_performance_feedback_flow():


    flow = IntelligenceFlow()


    consensus = ConsensusResult(

        trend="BULLISH",

        signal="BUY",

        confidence=85

    )


    report = flow.create_report(
        consensus
    )


    assert report.performance_feedback is not None


    assert report.performance_feedback["result"] == "SUCCESS"


    assert report.performance_feedback["score"] == 100