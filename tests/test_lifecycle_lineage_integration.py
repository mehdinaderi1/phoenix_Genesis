from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)

from intelligence.lifecycle.strategy_lineage_tracker import (
    StrategyLineageTracker
)


class MockEvolutionController:

    def evolve(self, strategy):

        return {
            "strategy": strategy + "_v2",
            "parent_strategy": strategy,
            "action": "IMPROVE",
            "status": "EVOLVED"
        }


def test_lifecycle_lineage_integration():

    repository = LifecycleEvolutionRepository()

    lineage = StrategyLineageTracker()

    controller = MockEvolutionController()


    base_strategy = "MomentumStrategy"


    lineage.register(
        base_strategy,
        generation=0
    )


    result = controller.evolve(
        base_strategy
    )


    repository.save(result)


    lineage.register(
        result["strategy"],
        parent_strategy=result["parent_strategy"],
        generation=1
    )


    record = repository.get_latest()


    assert record["strategy"] == "MomentumStrategy_v2"

    assert record["parent_strategy"] == "MomentumStrategy"


    assert lineage.get_parent(
        "MomentumStrategy_v2"
    ) == "MomentumStrategy"


    assert lineage.get_ancestry(
        "MomentumStrategy_v2"
    ) == [
        "MomentumStrategy_v2",
        "MomentumStrategy"
    ]