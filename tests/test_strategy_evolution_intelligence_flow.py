from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_strategy_evolution_in_intelligence_flow():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )


    report = flow.create_report(
        consensus
    )


    assert report.strategy_evolution is not None

    assert (
        "evolution"
        in report.strategy_evolution
    )