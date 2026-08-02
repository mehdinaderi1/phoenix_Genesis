from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.evolution.evolution_confidence import (
    EvolutionConfidence
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory
)


class DummyAnalytics:
    pass


class DummyRollback:

    def rollback(self, strategy):
        return strategy



def test_evolution_confidence_integration():


    history = EvolutionHistory()


    controller = SelfEvolutionController(

        evolution_engine=
            StrategyEvolutionEngine(
                history=history
            ),

        analytics=
            DummyAnalytics(),

        decision=
            EvolutionDecision(),

        rollback=
            DummyRollback(),

        history=
            history,

        confidence=
            EvolutionConfidence()

    )


    strategy = {

        "name":
            "momentum_strategy",

        "generation":
            1,

        "success_rate":
            0.85

    }


    result = controller.run(

        strategy,

        80

    )


    assert (
        result["confidence"]
        is not None
    )


    assert (
        result["confidence"]["confidence"]
        >
        50
    )


    assert (
        result["strategy"]["generation"]
        ==
        2
    )