from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)


class MockInsight:

    def __init__(
        self,
        learning
    ):
        self.learning = learning



class EvolutionDecisionAdapter:

    def __init__(self, decision):

        self.decision = decision


    def decide(
        self,
        insight,
        current_score,
        parent_score
    ):

        result = self.decision.decide(
            current_score,
            parent_score
        )


        if (
            insight.learning
            and result["decision"] == "KEEP"
        ):

            return {
                "decision": "IMPROVE",
                "reason": "learning signal active"
            }


        return result



def test_learning_signal_can_modify_keep_decision():

    adapter = EvolutionDecisionAdapter(
        EvolutionDecision()
    )


    result = adapter.decide(

        MockInsight(True),

        90,

        80

    )


    assert result["decision"] == "IMPROVE"



def test_normal_improvement_keeps_decision():

    adapter = EvolutionDecisionAdapter(
        EvolutionDecision()
    )


    result = adapter.decide(

        MockInsight(False),

        90,

        80

    )


    assert result["decision"] == "KEEP"



def test_degraded_strategy_rolls_back():

    adapter = EvolutionDecisionAdapter(
        EvolutionDecision()
    )


    result = adapter.decide(

        MockInsight(True),

        50,

        80

    )


    assert result["decision"] == "ROLLBACK"