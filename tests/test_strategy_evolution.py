from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)


def test_keep_good_strategy():

    engine = StrategyEvolutionEngine()

    result = engine.evaluate(
        {
            "score":85,
            "success_rate":0.8
        }
    )

    assert result["decision"] == "KEEP"



def test_retire_bad_strategy():

    engine = StrategyEvolutionEngine()

    result = engine.evaluate(
        {
            "score":40,
            "success_rate":0.2
        }
    )

    assert result["decision"] == "RETIRE"



def test_evolve_strategy():

    engine = StrategyEvolutionEngine()

    result = engine.evolve(
        "trend_following",
        80
    )

    assert result["evolved"] is True
    assert result["parent"] == "trend_following"