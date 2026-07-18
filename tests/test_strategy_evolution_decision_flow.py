from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)


def test_good_strategy_should_keep():

    decision = StrategyEvolutionDecision()

    result = decision.evaluate(
        "Trend",
        90
    )

    assert result["action"] == "KEEP"



def test_medium_strategy_should_evolve():

    decision = StrategyEvolutionDecision()

    result = decision.evaluate(
        "Trend",
        75
    )

    assert result["action"] == "EVOLVE"

    assert result["parent"] == "Trend"



def test_bad_strategy_should_retire():

    decision = StrategyEvolutionDecision()

    result = decision.evaluate(
        "Random",
        30
    )

    assert result["action"] == "RETIRE"