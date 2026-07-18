from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_quality_gate import StrategyQualityGate


class DummyStrategyScore:

    def __init__(
        self,
        strategy,
        score,
        samples,
        success_rate
    ):
        self.strategy = strategy
        self.score = score
        self.samples = samples
        self.success_rate = success_rate



def test_bad_strategy_rejected_by_quality_gate():

    memory = StrategyMemory()

    gate = StrategyQualityGate()

    updater = StrategyUpdate(
        memory,
        gate
    )

    bad_strategy = DummyStrategyScore(
        strategy="Random",
        score=30,
        samples=5,
        success_rate=0.2
    )

    result = updater.update(
        bad_strategy
    )

    assert result["updated"] is False
    assert result["reason"] == "quality_gate_failed"



def test_good_strategy_saved_by_quality_gate():

    memory = StrategyMemory()

    gate = StrategyQualityGate()

    updater = StrategyUpdate(
        memory,
        gate
    )

    good_strategy = DummyStrategyScore(
        strategy="Trend",
        score=85,
        samples=100,
        success_rate=0.75
    )

    result = updater.update(
        good_strategy
    )

    assert result["updated"] is True