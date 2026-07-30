from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)


def test_strategy_evolution_stores_governance_memory():

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


    assert (
        result["governance_memory_count"]
        == 1
    )