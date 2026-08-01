from intelligence.lifecycle.lifecycle_evolution_decision import (
    LifecycleEvolutionDecision
)


def test_low_score_without_history_improves():

    decision = LifecycleEvolutionDecision()

    result = decision.decide(
        40,
        {
            "has_history": False,
            "evolution_count": 0
        }
    )

    assert result == "IMPROVE"



def test_high_score_keeps_strategy():

    decision = LifecycleEvolutionDecision()

    result = decision.decide(
        90,
        {
            "has_history": True,
            "evolution_count": 1
        }
    )

    assert result == "KEEP"



def test_failed_repeated_evolution_archives():

    decision = LifecycleEvolutionDecision()

    result = decision.decide(
        35,
        {
            "has_history": True,
            "evolution_count": 3
        }
    )

    assert result == "ARCHIVE"



def test_unknown_case_goes_to_evaluate():

    decision = LifecycleEvolutionDecision()

    result = decision.decide(
        65,
        {
            "has_history": True,
            "evolution_count": 1
        }
    )

    assert result == "EVALUATE"