from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision,
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine,
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)



def create_real_controller():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine()

    decision = EvolutionDecision()

    rollback = RollbackEngine(
        history
    )


    controller = SelfEvolutionController(

        evolution_engine=engine,

        analytics=None,

        decision=decision,

        rollback=rollback

    )


    return controller, history



def test_real_strong_strategy_evolves():

    controller, history = create_real_controller()


    strategy = {

        "name": "trend_v1",

        "score": 85,

        "success_rate": 0.8

    }


    result = controller.run(

        strategy,

        strategy["score"]

    )


    assert result is not None



def test_real_weak_strategy_blocked():

    controller, history = create_real_controller()


    strategy = {

        "name": "bad_v1",

        "score": 40,

        "success_rate": 0.2

    }


    result = controller.run(

        strategy,

        strategy["score"]

    )


    assert result["action"] == "NO_EVOLUTION"