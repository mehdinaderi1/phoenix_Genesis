from intelligence.lifecycle.lifecycle_evolution_flow import (
    LifecycleEvolutionFlow
)

from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)


class MockDecisionEngine:

    def decide(self, strategy):
        return "IMPROVE"



class MockController:

    def execute(self, decision, strategy):

        return {
            "action": decision,
            "strategy": strategy + "_v2",
            "status": "EVOLVED"
        }



def test_evolution_result_saved_in_repository():

    repository = LifecycleEvolutionRepository()

    flow = LifecycleEvolutionFlow(
        lifecycle_decision_engine=MockDecisionEngine(),
        evolution_controller=MockController(),
        evolution_repository=repository
    )


    result = flow.execute(
        "Strategy"
    )


    assert result["strategy"] == "Strategy_v2"

    records = repository.get_all()

    assert len(records) == 1

    assert records[0]["action"] == "IMPROVE"

    assert records[0]["status"] == "EVOLVED"