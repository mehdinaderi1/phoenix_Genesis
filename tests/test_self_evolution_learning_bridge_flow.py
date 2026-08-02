from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def evolve(self, strategy, score):

        return {

            "evolved": True,

            "strategy": "strategy_v2",

            "generation": 2,

            "score": score + 15

        }



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



class MockLearningBridge:

    def __init__(self):

        self.called = False


    def evaluate(
        self,
        old_strategy,
        new_strategy,
        performance
    ):

        self.called = True


        return {

            "learning": True,

            "confidence": 0.9,

            "reason": "Low success rate"

        }



def test_self_evolution_learning_bridge_flow():

    history = MockHistory()

    memory = MockMemory()

    bridge = MockLearningBridge()


    controller = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=None,

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

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



def test_learning_bridge_contract():

    bridge = MockLearningBridge()


    result = bridge.evaluate(

        "strategy_v1",

        "strategy_v2",

        {

            "score": 50,

            "success_rate": 0.3

        }

    )


    assert bridge.called is True


    assert result["learning"] is True


    assert result["confidence"] == 0.9


    assert (
        result["reason"]
        ==
        "Low success rate"
    )