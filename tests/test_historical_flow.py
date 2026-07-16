from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_historical_context_in_flow():

    flow = IntelligenceFlow()


    report = flow.create_report(
        MockConsensus()
    )


    assert report.historical_context is not None

    assert report.historical_context.pattern is not None