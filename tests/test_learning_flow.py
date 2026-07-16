from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_learning_flow_integration():

    flow = IntelligenceFlow()


    report = flow.create_report(
        MockConsensus()
    )


    assert report is not None


    assert hasattr(
        report,
        "learning_insight"
    )


    insight = report.learning_insight


    assert insight is not None


    assert hasattr(
        insight,
        "reliability"
    )


    assert hasattr(
        insight,
        "samples"
    )


    assert hasattr(
        insight,
        "average_confidence"
    )