from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision,
)


class SpyEvolutionEngine:

    def __init__(self):
        self.calls = []

    def evolve(self, strategy, score):
        self.calls.append((strategy, score))
        raise AssertionError(
            "StrategyEvolutionDecision must not execute the evolution engine"
        )


def test_strategy_evolution_decision_keeps_high_score():
    engine = SpyEvolutionEngine()
    decision = StrategyEvolutionDecision(engine)

    result = decision.evaluate(
        {"name": "S", "score": 90},
        90,
    )

    assert result["action"] == "KEEP"
    assert result["strategy"] == {"name": "S", "score": 90}
    assert result["reason"] == "high performance"
    assert engine.calls == []


def test_strategy_evolution_decision_requests_evolution_without_execution():
    engine = SpyEvolutionEngine()
    decision = StrategyEvolutionDecision(engine)

    result = decision.evaluate(
        {"name": "S", "score": 75},
        75,
    )

    assert result["action"] == "EVOLVE"
    assert result["strategy"] == {"name": "S", "score": 75}
    assert result["parent"] == {"name": "S", "score": 75}
    assert result["reason"] == "performance can improve"
    assert engine.calls == []


def test_strategy_evolution_decision_retires_low_score():
    engine = SpyEvolutionEngine()
    decision = StrategyEvolutionDecision(engine)

    result = decision.evaluate(
        {"name": "S", "score": 40},
        40,
    )

    assert result["action"] == "RETIRE"
    assert result["strategy"] == {"name": "S", "score": 40}
    assert result["reason"] == "poor performance"
    assert engine.calls == []
