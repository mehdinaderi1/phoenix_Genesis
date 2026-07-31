from intelligence.flow import IntelligenceFlow


class DummyConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_report_contains_evolution_execution():

    flow = IntelligenceFlow()


    report = flow.create_report(
        DummyConsensus()
    )


    assert hasattr(
        report,
        "evolution_execution"
    )