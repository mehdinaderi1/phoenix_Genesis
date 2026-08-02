from dataclasses import dataclass



@dataclass
class LearningRecord:

    strategy: str
    lesson: str
    confidence: float
    learning: bool



class MockMemory:

    def __init__(self):

        self.records = []


    def store(self, record):

        self.records.append(record)


    def find_by_strategy(self, strategy):

        return [

            r
            for r in self.records

            if r.strategy == strategy

        ]



class EvolutionLearningRecall:

    def __init__(
        self,
        memory
    ):

        self.memory = memory


    def recall(
        self,
        strategy
    ):

        records = (
            self.memory.find_by_strategy(
                strategy
            )
        )


        return {

            "known": bool(records),

            "lessons": [

                r.lesson
                for r in records

            ],

            "confidence":

                max(

                    [
                        r.confidence
                        for r in records
                    ],

                    default=0

                )

        }



class EvolutionLearningContext:

    def __init__(
        self,
        recall
    ):

        self.recall = recall


    def build(
        self,
        strategy
    ):

        memory = self.recall.recall(
            strategy
        )


        return {

            "strategy": strategy,

            "has_history":
                memory["known"],

            "lessons":
                memory["lessons"],

            "confidence":
                memory["confidence"]

        }



def test_context_contains_previous_lessons():

    memory = MockMemory()


    memory.store(

        LearningRecord(

            strategy="strategy_v2",

            lesson="Improve entry conditions",

            confidence=0.9,

            learning=True

        )

    )


    recall = EvolutionLearningRecall(
        memory
    )


    context_engine = EvolutionLearningContext(
        recall
    )


    context = context_engine.build(
        "strategy_v2"
    )


    assert context["has_history"] is True


    assert (
        "Improve entry conditions"
        in context["lessons"]
    )


    assert context["confidence"] == 0.9



def test_context_for_new_strategy():

    memory = MockMemory()


    context_engine = EvolutionLearningContext(

        EvolutionLearningRecall(
            memory
        )

    )


    context = context_engine.build(
        "new_strategy"
    )


    assert context["has_history"] is False


    assert context["lessons"] == []


    assert context["confidence"] == 0



def test_context_can_support_future_decision():

    memory = MockMemory()


    memory.store(

        LearningRecord(

            strategy="strategy_v3",

            lesson="Reduce risk exposure",

            confidence=0.85,

            learning=True

        )

    )


    context_engine = EvolutionLearningContext(

        EvolutionLearningRecall(
            memory
        )

    )


    context = context_engine.build(
        "strategy_v3"
    )


    assert context["has_history"] is True

    assert (
        context["confidence"]
        >
        0.8
    )