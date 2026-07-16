from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"
    signal = "BUY"
    confidence = 85



def test_adaptive_confidence_in_flow():

    flow = IntelligenceFlow()

    report = flow.create_report(
        MockConsensus()
    )

    assert report is not None

    assert hasattr(
        report,
        "confidence"
    )

    assert report.confidence > 0