from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_quality_gate import StrategyQualityGate
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_score import StrategyScore



def test_strategy_quality_gate_blocks_bad_strategy():

    memory = StrategyMemory()

    gate = StrategyQualityGate()

    updater = StrategyUpdate(
        memory,
        gate
    )


    bad_strategy = StrategyScore(
        "Random",
        30
    )


    result = updater.update(
        bad_strategy
    )


    assert result["updated"] is False
    assert result["reason"] == "quality_gate_failed"



def test_strategy_quality_gate_allows_good_strategy():

    memory = StrategyMemory()

    gate = StrategyQualityGate(
        min_samples=0
    )

    updater = StrategyUpdate(
        memory,
        gate
    )


    good_strategy = StrategyScore(
        "Trend",
        85
    )


    good_strategy.samples = 50
    good_strategy.success_rate = 0.8


    result = updater.update(
        good_strategy
    )


    assert result["updated"] is True
    assert result["strategy"] == "Trend"