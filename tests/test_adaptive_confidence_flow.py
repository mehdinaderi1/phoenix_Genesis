from intelligence.flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"
    signal = "BUY"
    confidence = 70



def test_adaptive_confidence_in_flow_with_champion_strategy():

    flow = IntelligenceFlow()


    flow.strategy_memory.store(
        {
            "strategy": "TREND_BUY_LOW",
            "name": "TREND_BUY_LOW",
            "regime": "RANGING",
            "signal": "BUY",
            "risk": "MEDIUM",
            "score": 90,
            "success_rate": 0.9,
            "samples": 50,
            "status": "ACTIVE"
        }
    )


    report = flow.create_report(
        MockConsensus()
    )


    assert report is not None


    assert report.champion_strategy is not None


    assert report.confidence > 70