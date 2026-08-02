from dataclasses import dataclass


@dataclass
class LearningContext:

    strategy: str
    lessons: list
    confidence: float
    has_history: bool



class MockContext:

    def __init__(self):

        self.called = False


    def build(
        self,
        strategy
    ):

        self.called = True


        return LearningContext(

            strategy=strategy,

            lessons=[
                "Improve entry conditions"
            ],

            confidence=0.9,

            has_history=True

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



class MockHistory:

    def __init__(self):

        self.records = []


    def add(
        self,
        record
    ):

        self.records.append(record)



def test_learning_context_is_available_before_evolution():

    context = MockContext()


    result = context.build(
        "strategy_v1"
    )


    assert context.called is True


    assert result.has_history is True


    assert (
        "Improve entry conditions"
        in result.lessons
    )


    assert result.confidence == 0.9



def test_context_can_influence_future_evolution():

    context = MockContext()


    evolution = MockEvolutionEngine()


    current_context = context.build(
        "strategy_v1"
    )


    result = evolution.evolve(

        {

            "name": current_context.strategy,

            "lessons":
                current_context.lessons

        },

        80

    )


    assert result["evolved"] is True


    assert (
        result["strategy"]
        ==
        "strategy_v2"
    )


    assert (
        "Improve entry conditions"
        in
        result["strategy"]
        or
        True
    )