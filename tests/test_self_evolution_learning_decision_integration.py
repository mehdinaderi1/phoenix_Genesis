from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)



class MockEvolutionEngine:

    def evolve(
        self,
        strategy,
        score
    ):

        return {

            "evolved": True,

            "strategy": "strategy_v2",

            "generation": 2,

            "score": score + 10

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



class MockLearningAdapter:

    def __init__(self):

        self.called = False


    def decide(
        self,
        decision,
        learning_context
    ):

        self.called = True


        return {

            "decision": "KEEP",

            "reason":
                "confirmed by previous learning",

            "learning_applied": True

        }



class MockRollback:

    def rollback(
        self,
        strategy
    ):

        return {

            "rolled_back": True

        }



class MockLearningContext:

    def build(
        self,
        strategy
    ):

        return {

            "has_history": True,

            "confidence": 0.95

        }



def test_controller_uses_learning_decision_adapter():


    adapter = MockLearningAdapter()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        learning_context=
            MockLearningContext(),

        learning_decision_adapter=
            adapter

    )


    result = controller.run(

        {

            "name":
                "strategy_v1"

        },

        80

    )


    assert adapter.called is True


    assert (
        result["decision"]["decision"]
        ==
        "KEEP"
    )


    assert (
        result["decision"]["learning_applied"]
        is True
    )



def test_controller_without_adapter_keeps_old_flow():


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback()

    )


    result = controller.run(

        {

            "name":
                "strategy_v1"

        },

        80

    )


    assert (
        result["decision"]["decision"]
        ==
        "KEEP"
    )