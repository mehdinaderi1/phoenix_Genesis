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


    def all(self):

        return self.records


    def find_by_strategy(
        self,
        strategy
    ):

        return [

            r
            for r in self.records

            if r.strategy == strategy

        ]



def test_learning_memory_stores_evolution_lesson():

    memory = EvolutionLearningMemory()


    record = LearningRecord(

        strategy="strategy_v2",

        lesson="Improve entry conditions",

        confidence=0.9,

        learning=True

    )


    memory.store(record)


    records = memory.all()


    assert len(records) == 1


    assert records[0].strategy == "strategy_v2"

    assert records[0].lesson == "Improve entry conditions"



def test_learning_memory_queries_strategy_history():

    memory = EvolutionLearningMemory()


    memory.store(

        LearningRecord(

            strategy="strategy_v2",

            lesson="Reduce risk",

            confidence=0.8,

            learning=True

        )

    )


    memory.store(

        LearningRecord(

            strategy="strategy_v3",

            lesson="Optimize parameters",

            confidence=0.85,

            learning=True

        )

    )


    result = memory.find_by_strategy(
        "strategy_v2"
    )


    assert len(result) == 1


    assert result[0].lesson == "Reduce risk"



def test_learning_memory_keeps_confidence_signal():

    memory = EvolutionLearningMemory()


    record = LearningRecord(

        strategy="strategy_v4",

        lesson="Stable strategy",

        confidence=0.95,

        learning=False

    )


    memory.store(record)


    saved = memory.all()[0]


    assert saved.confidence == 0.95

    assert saved.learning is False