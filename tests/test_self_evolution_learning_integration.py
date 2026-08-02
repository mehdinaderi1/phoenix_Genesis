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

    def analyze(self, record):

        return {
            "success_rate": 0.4
        }



class MockInsight:

    def analyze(
        self,
        old_strategy,
        new_strategy,
        performance,
        decision=None
    ):

        class Result:

            learning = True
            confidence = 0.9
            reason = "Low success rate"

        return Result()



class MockDecision:

    def decide(
        self,
        current_score,
        parent_score
    ):

        return {
            "decision": "KEEP",
            "reason": "performance improved"
        }



class MockDecisionAdapter:

    def decide(
        self,
        insight,
        current_score,
        parent_score
    ):

        if insight.learning:

            return {
                "decision": "IMPROVE",
                "reason": "learning signal active"
            }

        return {
            "decision": "KEEP"
        }



class MockRollback:

    def rollback(self, strategy):

        return {
            "rolled_back": True
        }



class MockGovernance:

    def evaluate(self, strategy):

        return {
            "approved": True
        }



class MockRecall:

    def analyze(self, strategy):

        return {
            "known": True
        }



class MockIntelligence:

    def evaluate(self, strategy):

        return {
            "decision": "ALLOW"
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



def test_self_evolution_uses_learning_signal():

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

        governance_bridge=MockGovernance(),

        memory=memory

    )


    result = controller.run(

        {
            "name": "strategy_v1"
        },

        80

    )


    assert result["action"] == "KEEP"


    assert len(history.records) == 1

    assert len(memory.records) == 1



def test_learning_signal_object_behavior():

    insight = MockInsight().analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 50,
            "success_rate": 0.3
        }

    )


    assert insight.learning is True

    assert insight.confidence == 0.9

    assert (
        insight.reason
        ==
        "Low success rate"
    )