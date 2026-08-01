from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)

from intelligence.lifecycle.lifecycle_evolution_recall import (
    LifecycleEvolutionRecall
)

from intelligence.lifecycle.lifecycle_evolution_context import (
    LifecycleEvolutionContext
)

from intelligence.lifecycle.lifecycle_evolution_decision import (
    LifecycleEvolutionDecision
)


class MockController:

    def execute(self, decision, strategy):

        if decision == "IMPROVE":
            return {
                "strategy": strategy + "_v2",
                "parent_strategy": strategy,
                "action": decision,
                "status": "EVOLVED"
            }

        return {
            "strategy": strategy,
            "parent_strategy": None,
            "action": decision,
            "status": "UNCHANGED"
        }



def test_phoenix_self_evolution_cycle():

    repository = LifecycleEvolutionRepository()

    recall = LifecycleEvolutionRecall(
        repository
    )

    context_builder = LifecycleEvolutionContext(
        recall
    )

    decision_engine = LifecycleEvolutionDecision()

    controller = MockController()


    strategy = "MomentumStrategy"


    context = context_builder.build(
        strategy
    )


    decision = decision_engine.decide(
        40,
        context
    )


    result = controller.execute(
        decision,
        strategy
    )


    repository.save(
        result
    )


    history = recall.recall(
        strategy
    )


    assert decision == "IMPROVE"

    assert result["strategy"] == "MomentumStrategy_v2"

    assert result["status"] == "EVOLVED"

    assert len(history) == 1