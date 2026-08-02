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



class MockRollback:

    def rollback(
        self,
        strategy
    ):

        return {

            "rolled_back": True

        }



class MockLearningContext:

    def __init__(self):

        self.called = False


    def build(
        self,
        strategy
    ):

        self.called = True


        return {

            "has_history": True,

            "lessons": [

                "Improve entry conditions"

            ],

            "confidence": 0.9

        }



class MockHistory:

    def __init__(self):

        self.records = []


    def add(
        self,
        record
    ):

        self.records.append(record)



def test_controller_accepts_learning_context():

    context = MockLearningContext()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        history=
            MockHistory(),

        learning_context=context

    )


    result = controller.run(

        {

            "name": "strategy_v1"

        },

        80

    )


    assert result["action"] == "KEEP"


    assert context.called is True



def test_learning_context_is_returned():

    context = MockLearningContext()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        learning_context=context

    )


    result = controller.run(

        {

            "name": "strategy_v1"

        },

        80

    )


    assert (
        result["learning_context"]
        ["has_history"]
        is True
    )


    assert (
        result["learning_context"]
        ["confidence"]
        ==
        0.9
    )