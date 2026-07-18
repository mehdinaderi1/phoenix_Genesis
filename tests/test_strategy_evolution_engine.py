from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)


def test_strategy_evolution():

    engine = StrategyEvolutionEngine()


    result = engine.evolve(
        "Trend",
        80
    )


    assert result["strategy"] == "Trend_v2"

    assert result["parent"] == "Trend"

    assert result["score"] == 90

    assert result["generation"] == 2