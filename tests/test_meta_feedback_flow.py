from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult



def test_meta_feedback_stored_in_flow_memory():

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
        "meta_feedback"
    )


    assert report.meta_feedback is not None


    assert (
        flow.meta_memory.count()
        == 1
    )


    stored = (
        flow.meta_memory
        .get_records()[0]
    )


    assert (
        stored.outcome
        in [
            "SUCCESS",
            "FAILED"
        ]
    )


    assert (
        stored.confidence_after
        ==
        report.confidence
    )

def test_meta_feedback_flows_into_next_meta_intelligence_cycle():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )


    first_report = flow.create_report(
        consensus
    )


    assert (
        flow.meta_memory.count()
        == 1
    )


    second_report = flow.create_report(
        consensus
    )

    assert (
        flow.meta_memory.count()
        == 2
    )


    assert second_report.meta_insight is not None


    assert (
        second_report.meta_insight.meta_feedback["samples"]
        == flow.meta_memory.count()
    )