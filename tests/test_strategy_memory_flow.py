from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_strategy_memory_flow():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(

        trend="BULLISH",

        signal="BUY",

        confidence=85

    )


    report = flow.create_report(
        consensus
    )


    assert report.strategy_insight is not None


    assert flow.strategy_memory.count() == 1


    record = flow.strategy_memory.latest()


    print(flow.strategy_memory.records)
    print(report.learned_strategies)
    
    assert record is not None