from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)


class DummyAnalytics:
    pass


class DummyRollback:

    def rollback(self, strategy):
        return strategy



def test_self_evolution_closed_loop():

    memory = EvolutionMemory()

    history = EvolutionHistory()


    engine = StrategyEvolutionEngine(
        history=history
    )


    controller = SelfEvolutionController(

        evolution_engine=engine,

        analytics=DummyAnalytics(),

        decision=EvolutionDecision(),

        rollback=DummyRollback(),

        history=history,

        memory=memory
    )


    # -------------------------
    # Evolution 1
    # -------------------------

    strategy = {

        "name": "momentum_strategy",

        "generation": 1

    }


    first = controller.run(

        strategy,

        70

    )


    assert first["action"] == "KEEP"


    assert (
        first["strategy"]["strategy"]
        ==
        "momentum_strategy_v2"
    )


    assert (
        first["strategy"]["generation"]
        ==
        2
    )


    # Memory updated

    assert memory.count() == 1


    first_record = memory.latest(
        "momentum_strategy_v2"
    )


    assert first_record is not None



    # -------------------------
    # Feedback / Learning
    # -------------------------

    improved_score = (
        first_record.score_after + 10
    )


    learned_strategy = {

        "name": "momentum_strategy",

        "generation": 2

    }



    # -------------------------
    # Evolution 2
    # -------------------------

    second = controller.run(

        learned_strategy,

        improved_score

    )


    assert second["action"] == "KEEP"


    assert (
        second["strategy"]["generation"]
        >
        first["strategy"]["generation"]
    )


    assert (
        second["strategy"]["score"]
        >
        first["strategy"]["score"]
    )