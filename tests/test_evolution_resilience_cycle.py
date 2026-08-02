from intelligence.evolution.self_evolution_controller import SelfEvolutionController
from intelligence.evolution.rollback import RollbackManager
from intelligence.memory.governance_memory import GovernanceMemory


def test_evolution_resilience_cycle():

    memory = GovernanceMemory()

    rollback = RollbackManager()

    controller = SelfEvolutionController(
        rollback_manager=rollback,
        memory=memory
    )

    # Generation 2 created but performance degraded
    bad_evolution = {
        "strategy": "momentum_strategy_v2",
        "generation": 2,
        "performance_score": 0.35,
        "success_rate": 0.40,
        "confidence": 45
    }

    result = controller.evaluate_evolution(
        bad_evolution
    )

    # Governor blocks bad evolution
    assert result.blocked is True

    # Rollback executed
    assert rollback.executed is True

    # Failure stored in memory
    assert memory.count() == 1

    failure_recorded = memory.latest()

    assert failure_recorded is not None
    assert failure_recorded.status == "FAILED"

    # System does not continue with bad strategy
    next_decision = controller.next_action()

    assert next_decision == "HOLD"