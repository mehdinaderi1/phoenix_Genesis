from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)


def test_good_strategy_should_keep():

    engine = StrategyEvolutionEngine()

    strategy = {
        "score": 90,
        "success_rate": 0.8
    }

    result = engine.evaluate(strategy)

    assert result["decision"] == "KEEP"



def test_medium_strategy_should_improve():

    engine = StrategyEvolutionEngine()

    strategy = {
        "score": 65,
        "success_rate": 0.5
    }

    result = engine.evaluate(strategy)

    assert result["decision"] == "IMPROVE"



def test_bad_strategy_should_retire():

    engine = StrategyEvolutionEngine()

    strategy = {
        "score": 30,
        "success_rate": 0.2
    }

    result = engine.evaluate(strategy)

    assert result["decision"] == "RETIRE"