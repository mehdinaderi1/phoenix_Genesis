from intelligence.learning.strategy_quality_gate import (
    StrategyQualityGate
)


def test_strategy_quality_gate_accepts_good_strategy():

    gate = StrategyQualityGate()

    strategy = {
        "strategy": "Trend",
        "score": 80,
        "samples": 50,
        "success_rate": 0.7
    }

    assert gate.validate(strategy) is True



def test_strategy_quality_gate_rejects_bad_strategy():

    gate = StrategyQualityGate()

    strategy = {
        "strategy": "Random",
        "score": 30,
        "samples": 5,
        "success_rate": 0.2
    }

    assert gate.validate(strategy) is False