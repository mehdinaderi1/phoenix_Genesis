from datetime import datetime, timezone

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)


class MockEvolutionEngine:

    def evolve(self, strategy, score):

        return {
            "evolved": True,
            "strategy": strategy["name"] + "_v2",
            "generation": 2,
            "score": 90,
        }


class MockDecision:

    def decide(self, new_score, old_score):

        return {
            "decision": "KEEP"
        }


class MockRollback:

    def rollback(self, strategy):

        return {
            "status": "ROLLED_BACK"
        }


class MockGovernanceBridge:

    def evaluate(self, strategy):

        return {
            "approved": True
        }



def test_self_evolution_controller_end_to_end():

    history = EvolutionHistory()


    controller = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=None,

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

        governance_bridge=MockGovernanceBridge()

    )


    result = controller.run(

        strategy={
            "name": "MomentumStrategy"
        },

        score=80

    )


    assert result["action"] == "KEEP"


    assert len(history.all()) == 1


    record = history.latest()


    assert record.parent == (
        "MomentumStrategy"
    )


    assert record.child == (
        "MomentumStrategy_v2"
    )


    assert record.score_before == 80


    assert record.score_after == 90