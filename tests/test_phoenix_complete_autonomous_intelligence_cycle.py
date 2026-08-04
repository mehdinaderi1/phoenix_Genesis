from intelligence.intelligence_flow import IntelligenceFlow


class MockConsensus:

    trend = "BULLISH"

    confidence = 85

    signals = [
        "RSI bullish",
        "MACD crossover",
        "MA alignment"
    ]


def test_phoenix_complete_autonomous_intelligence_cycle():

    flow = IntelligenceFlow()

    consensus = MockConsensus()

    report = flow.create_report(
        consensus
    )


    # 1 - Market Intelligence
    assert report.symbol == "BTCUSDT"


    # 2 - Decision Intelligence
    assert hasattr(
        report,
        "confidence"
    )

    assert report.confidence >= 0


    # 3 - Evolution Intelligence
    assert hasattr(
        report,
        "evolution"
    )


    # 4 - Memory Layer
    assert hasattr(
        flow,
        "decision_memory"
    )


    # 5 - Experience Learning
    assert hasattr(
        flow,
        "experience_memory"
    )


    # 6 - Strategy Intelligence
    assert hasattr(
        flow,
        "strategy_memory"
    )


    # 7 - Governance
    assert hasattr(
        flow,
        "governance_memory"
    )


    # 8 - Self Evolution
    assert hasattr(
        flow,
        "self_evolution_controller"
    )


    # Final Phoenix Health Check

    assert report is not None