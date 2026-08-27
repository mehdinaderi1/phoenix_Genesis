from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"
    signal = "BUY"
    confidence = 85



def test_meta_intelligence_attached_to_report():

    flow = IntelligenceFlow()


    report = flow.create_report(
        MockConsensus()
    )


    assert report is not None


    assert hasattr(
        report,
        "meta_insight"
    )


    assert report.meta_insight is not None


    assert report.meta_insight.samples > 0