from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)


def test_strategy_evolution_contains_governance():

    flow = StrategyEvolutionFlow()


    result = flow.evaluate(
        "Trend",
        [
            {
                "score": 90,
                "success": True
            }
        ]
    )


    assert "governance" in result
    assert result["governance"]["approved"] is True