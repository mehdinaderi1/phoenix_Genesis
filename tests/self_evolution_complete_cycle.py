from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def evolve(self, strategy, score):

        return {
            "evolved": True,
            "strategy": "strategy_v2",
            "generation": 2,
            "score": score + 10
        }


class MockAnalytics:
    pass


class MockDecision:

    def decide(self, new_score, parent_score):

        return {
            "decision": "ACCEPT",
            "confidence": 90
        }


class MockRollback:

    def rollback(self, strategy):

        return {
            "rolled_back": True,
            "strategy": strategy
        }


class MockGovernanceBridge:

    def evaluate(self, strategy):

        return {
            "approved": True,
            "reason": "approved"
        }


class MockRecall:

    def analyze(self, strategy):

        return {
            "known": True,
            "similarity": 0.85
        }


class MockIntelligence:

    def evaluate(self, strategy):

        return {
            "decision": "ALLOW",
            "confidence": 90
        }


class MockHistory:

    def __init__(self):
        self.records = []

    def add(self, record):

        self.records.append(record)


class MockMemory:

    def __init__(self):
        self.records = []

    def store(self, record):

        self.records.append(record)


def test_self_evolution_complete_cycle():

    history = MockHistory()
    memory = MockMemory()

    controller = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=MockAnalytics(),

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

        recall=MockRecall(),

        intelligence=MockIntelligence(),

        governance_bridge=MockGovernanceBridge(),

        memory=memory

    )


    strategy = {

        "name": "strategy_v1"

    }


    result = controller.run(

        strategy,

        score=80

    )


    assert result["action"] == "ACCEPT"


    assert result["strategy"]["evolved"] is True


    assert result["recall"]["known"] is True


    assert result["intelligence"]["decision"] == "ALLOW"


    assert len(history.records) == 1


    assert len(memory.records) == 1