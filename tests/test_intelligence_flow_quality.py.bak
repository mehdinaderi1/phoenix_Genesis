from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"

    signal = "BUY"

    confidence = 85



def test_intelligence_flow_quality():

    flow = IntelligenceFlow()


    report = flow.create_report(
        MockConsensus()
    )


    records = flow.decision_memory.records


    assert len(records) == 1


    record = records[0]


    assert record.symbol == "BTCUSDT"

    assert record.action is not None

    assert record.quality_score > 0