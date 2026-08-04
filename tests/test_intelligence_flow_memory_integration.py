from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_outcome_to_strategy_performance_memory_flow():

    flow = IntelligenceFlow()

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    report = flow.create_report(
        consensus
    )

    assert len(
        flow.outcome_memory.records
    ) == 1

    assert len(
        flow.strategy_performance_memory.records
    ) == 1

    performance = (
        flow.strategy_performance_memory.records[0]
    )

    assert performance.strategy is not None

    assert isinstance(
        performance.success,
        bool
    )