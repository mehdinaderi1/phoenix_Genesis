from intelligence.flow import IntelligenceFlow


class DummyConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_report_contains_self_evolution_status():

    flow = IntelligenceFlow()


    report = flow.create_report(
        DummyConsensus()
    )


    assert hasattr(
        report,
        "self_evolution"
    )


    assert (
        report.self_evolution["status"]
        == "READY"
    )


    assert (
        report.self_evolution["controller"]
        is True
    )