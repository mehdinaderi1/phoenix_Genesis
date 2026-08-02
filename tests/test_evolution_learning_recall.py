from dataclasses import dataclass



@dataclass
class LearningRecord:

    strategy: str
    lesson: str
    confidence: float
    learning: bool



class EvolutionLearningMemory:

    def __init__(self):

        self.records = []


    def store(self, record):

        self.records.append(record)


    def find_by_strategy(
        self,
        strategy
    ):

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


        if not records:

            return {

                "known": False,

                "lessons": [],

                "confidence": 0

            }


        return {

            "known": True,

            "lessons": [

                r.lesson
                for r in records

            ],

            "confidence": max(

                r.confidence
                for r in records

            )

        }



def test_recall_returns_previous_learning():

    memory = EvolutionLearningMemory()


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


    result = recall.recall(
        "strategy_v2"
    )


    assert result["known"] is True


    assert (
        "Improve entry conditions"
        in result["lessons"]
    )


    assert result["confidence"] == 0.9



def test_recall_handles_unknown_strategy():

    memory = EvolutionLearningMemory()


    recall = EvolutionLearningRecall(
        memory
    )


    result = recall.recall(
        "unknown_strategy"
    )


    assert result["known"] is False


    assert result["lessons"] == []


    assert result["confidence"] == 0



def test_recall_selects_best_confidence():

    memory = EvolutionLearningMemory()


    memory.store(

        LearningRecord(

            strategy="strategy_v3",

            lesson="Reduce risk",

            confidence=0.7,

            learning=True

        )

    )


    memory.store(

        LearningRecord(

            strategy="strategy_v3",

            lesson="Optimize parameters",

            confidence=0.95,

            learning=True

        )

    )


    recall = EvolutionLearningRecall(
        memory
    )


    result = recall.recall(
        "strategy_v3"
    )


    assert result["known"] is True


    assert (
        result["confidence"]
        ==
        0.95
    )


    assert len(result["lessons"]) == 2