from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"
    signal = "BUY"
    confidence = 85



def test_intelligence_context_in_report():

    flow = IntelligenceFlow()

    report = flow.create_report(
        MockConsensus()
    )


    assert report.intelligence_context is not None

    assert report.intelligence_context.adaptive_confidence > 0

    assert report.intelligence_context.historical_context is not None