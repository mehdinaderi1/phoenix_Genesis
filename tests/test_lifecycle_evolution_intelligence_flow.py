from intelligence.lifecycle.lifecycle_evolution_intelligence_flow import (
    LifecycleEvolutionIntelligenceFlow
)


class MockContext:

    def build(self, strategy):
        return {
            "has_history": False,
            "evolution_count": 0
        }


class MockDecision:

    def decide(self, score, context):
        return "IMPROVE"


class MockController:

    def execute(self, decision, strategy):
        return {
            "action": decision,
            "strategy": strategy + "_v2",
            "status": "EVOLVED"
        }


class MockRepository:

    def __init__(self):
        self.records = []

    def save(self, result):
        self.records.append(result)



def test_intelligence_flow_creates_new_strategy():

    repository = MockRepository()

    flow = LifecycleEvolutionIntelligenceFlow(
        MockContext(),
        MockDecision(),
        MockController(),
        repository
    )

    result = flow.execute(
        "Strategy",
        40
    )

    assert result["action"] == "IMPROVE"
    assert result["strategy"] == "Strategy_v2"

    assert len(repository.records) == 1