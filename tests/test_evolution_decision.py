from intelligence.evolution.evolution_decision import (
    EvolutionDecision,
)



def test_keep_when_improved():

    decision = EvolutionDecision()


    result = decision.decide(
        current_score=90,
        parent_score=80,
    )


    assert result["decision"] == "KEEP"



def test_rollback_when_degraded():

    decision = EvolutionDecision()


    result = decision.decide(
        current_score=60,
        parent_score=80,
    )


    assert result["decision"] == "ROLLBACK"