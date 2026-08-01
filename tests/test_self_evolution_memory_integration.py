from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)



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


    def rollback(
        self,
        strategy
    ):

        return strategy



def test_self_evolution_memory_integration():

    history = EvolutionHistory()

    memory = EvolutionMemory()


    controller = SelfEvolutionController(

        evolution_engine=StrategyEvolutionEngine(),

        analytics=None,

        decision=DummyDecision(),

        rollback=DummyRollback(),

        history=history,

        memory=memory

    )


    strategy = {

        "name": "trend_v1",

        "score": 85,

        "generation": 1

    }


    result = controller.run(

        strategy,

        85

    )


    assert result is not None

    assert memory.count() == 1

    assert history.latest() is not None