from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)


class DummyAnalytics:

    pass


class DummyDecision:


    def decide(
        self,
        new_score,
        old_score
    ):

        return {
            "decision": "KEEP"
        }


class DummyRollback:

    pass



def test_self_evolution_records_history():

    history = EvolutionHistory()


    engine = StrategyEvolutionEngine()


    controller = SelfEvolutionController(

        evolution_engine=engine,

        analytics=DummyAnalytics(),

        decision=DummyDecision(),

        rollback=DummyRollback(),

        history=history

    )


    strategy = {

        "name": "trend_v1",

        "score": 85,

        "success_rate": 0.8,

        "generation": 1

    }


    result = controller.run(

        strategy,

        strategy["score"]

    )


    record = history.latest()


    assert result is not None

    assert record is not None

    assert record.parent == "trend_v1"

    assert record.child == "trend_v1_v2"

    assert record.generation == 2