from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def __init__(self):
        self.calls = 0

    def evolve(
        self,
        strategy,
        score
    ):

        self.calls += 1

        return {

            "evolved": True,

            "strategy":
                strategy["name"] + f"_v{self.calls+1}",

            "generation":
                self.calls + 1,

            "score":
                score + 10

        }



class MockDecision:

    def decide(
        self,
        current_score,
        parent_score
    ):

        return {

            "decision":
                "KEEP",

            "reason":
                "performance improved"

        }



class MockFeedback:

    def __init__(self):

        self.memory = []


    def process(
        self,
        strategy,
        result
    ):

        record = {

            "strategy":
                strategy,

            "lesson":
                "successful evolution",

            "confidence":
                0.95

        }


        self.memory.append(
            record
        )


        return {

            "stored":
                True,

            "record":
                record

        }



class MockLearningContext:


    def __init__(self, feedback):

        self.feedback = feedback


    def build(
        self,
        strategy
    ):

        records = [

            r
            for r in self.feedback.memory

            if r["strategy"] == strategy

        ]


        return {

            "has_history":
                bool(records),

            "confidence":
                records[0]["confidence"]
                if records
                else 0

        }



class MockRollback:

    def rollback(
        self,
        strategy
    ):

        return {

            "rolled_back":
                True

        }



def build_controller(
    feedback
):

    return SelfEvolutionController(

        evolution_engine=
            MockEvolutionEngine(),

        analytics=None,

        decision=
            MockDecision(),

        rollback=
            MockRollback(),

        feedback=
            feedback,

        learning_context=
            MockLearningContext(
                feedback
            )

    )



def test_first_evolution_creates_learning_memory():


    feedback = MockFeedback()


    controller = build_controller(
        feedback
    )


    result = controller.run(

        {

            "name":
                "strategy"

        },

        80

    )


    assert (
        result["feedback"]["stored"]
        is True
    )


    assert len(
        feedback.memory
    ) == 1



def test_second_evolution_uses_previous_learning():


    feedback = MockFeedback()


    controller = build_controller(
        feedback
    )


    controller.run(

        {

            "name":
                "strategy"

        },

        80

    )


    context = (
        controller.learning_context.build(
            "strategy"
        )
    )


    assert (
        context["has_history"]
        is True
    )


    assert (
        context["confidence"]
        ==
        0.95
    )



def test_self_improving_cycle_is_closed():


    feedback = MockFeedback()


    controller = build_controller(
        feedback
    )


    first = controller.run(

        {

            "name":
                "strategy"

        },

        80

    )


    second_context = (
        controller.learning_context.build(
            "strategy"
        )
    )


    assert (
        first["feedback"]["stored"]
        is True
    )


    assert (
        second_context["has_history"]
        is True
    )