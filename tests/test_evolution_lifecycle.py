from intelligence.evolution.evolution_history import (
    EvolutionHistory
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def evolve(self, strategy, score):

        return {
            "evolved": True,
            "strategy": "trend_v2",
            "generation": 2,
            "score": 88
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



def test_full_evolution_lifecycle():

    history = EvolutionHistory()


    lifecycle = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=None,

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

        governance_bridge=MockGovernanceBridge()

    )


    result = lifecycle.run(

        strategy={
            "name": "trend_v1"
        },

        score=72

    )


    assert result["action"] == (
        "KEEP"
    )


    assert len(history.all()) == 1


    record = history.latest()


    assert record.child == (
        "trend_v2"
    )


    assert record.score_before == 72


    assert record.score_after == 88