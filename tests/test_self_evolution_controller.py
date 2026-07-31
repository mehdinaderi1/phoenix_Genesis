from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics,
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



def test_self_evolution_flow():

    history = EvolutionHistory()


    engine = StrategyEvolutionEngine(
        history=history
    )


    controller = SelfEvolutionController(
        evolution_engine=engine,
        analytics=EvolutionAnalytics(history),
        decision=EvolutionDecision(),
        rollback=RollbackEngine(history),
    )


    result = controller.run(
        "trend",
        80
    )


    assert result["action"] == "KEEP"


    assert (
        history.latest().child
        == "trend_v2"
    )