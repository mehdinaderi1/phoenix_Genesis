from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)


def test_strategy_evolution_flow_keep():

    flow = StrategyEvolutionFlow()

    history = [
        {
            "strategy": "Trend",
            "score": 90,
            "success": True
        },
        {
            "strategy": "Trend",
            "score": 95,
            "success": True
        }
    ]

    result = flow.evaluate(
        "Trend",
        history
    )

    assert result["evolution"]["action"] == "KEEP"



def test_strategy_evolution_flow_evolve():

    flow = StrategyEvolutionFlow()

    history = [
        {
            "strategy": "Trend",
            "score": 75,
            "success": True
        },
        {
            "strategy": "Trend",
            "score": 70,
            "success": True
        }
    ]

    result = flow.evaluate(
        "Trend",
        history
    )

    assert result["evolution"]["action"] == "EVOLVE"



def test_strategy_evolution_flow_retire():

    flow = StrategyEvolutionFlow()

    history = [
        {
            "strategy": "Random",
            "score": 30,
            "success": False
        },
        {
            "strategy": "Random",
            "score": 40,
            "success": False
        }
    ]

    result = flow.evaluate(
        "Random",
        history
    )

    assert result["evolution"]["action"] == "RETIRE"