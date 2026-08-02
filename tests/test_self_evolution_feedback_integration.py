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



class MockFeedback:

    def __init__(self):

        self.called = False

        self.received = None


    def process(
        self,
        strategy,
        result
    ):

        self.called = True

        self.received = {

            "strategy": strategy,

            "result": result

        }


        return {

            "stored": True

        }



def test_controller_calls_feedback_after_evolution():


    feedback = MockFeedback()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        feedback=
            feedback

    )


    result = controller.run(

        {

            "name":
                "strategy_v1"

        },

        80

    )


    assert (
        result["action"]
        ==
        "KEEP"
    )


    assert feedback.called is True


    assert (
        feedback.received["strategy"]
        ==
        "strategy_v1"
    )



def test_feedback_receives_evolution_result():


    feedback = MockFeedback()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        feedback=
            feedback

    )


    controller.run(

        {

            "name":
                "strategy_v1"

        },

        90

    )


    assert (
        feedback.received["result"]["evolved"]
        is True
    )
    
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



class MockFeedback:

    def __init__(self):

        self.called = False

        self.received = None


    def process(
        self,
        strategy,
        result
    ):

        self.called = True

        self.received = {

            "strategy": strategy,

            "result": result

        }


        return {

            "stored": True

        }



def test_controller_calls_feedback_after_evolution():


    feedback = MockFeedback()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        feedback=
            feedback

    )


    result = controller.run(

        {

            "name":
                "strategy_v1"

        },

        80

    )


    assert (
        result["action"]
        ==
        "KEEP"
    )


    assert feedback.called is True


    assert (
        feedback.received["strategy"]
        ==
        "strategy_v1"
    )



def test_feedback_receives_evolution_result():


    feedback = MockFeedback()


    controller = SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        feedback=
            feedback

    )


    controller.run(

        {

            "name":
                "strategy_v1"

        },

        90

    )


    assert (
        feedback.received["result"]["evolved"]
        is True
    )