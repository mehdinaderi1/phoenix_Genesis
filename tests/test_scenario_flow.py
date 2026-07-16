from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_scenario_in_report():

    flow = IntelligenceFlow()


    report = flow.create_report(
        MockConsensus()
    )


    assert report is not None


    assert hasattr(
        report,
        "scenarios"
    )


    assert report.scenarios is not None


    assert len(
        report.scenarios
    ) > 0