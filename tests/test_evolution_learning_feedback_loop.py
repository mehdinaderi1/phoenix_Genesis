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


    def store(
        self,
        record
    ):

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



class EvolutionLearningFeedback:


    def __init__(
        self,
        memory
    ):

        self.memory = memory



    def process(
        self,
        strategy,
        result
    ):


        if result["success"]:

            record = LearningRecord(

                strategy=strategy,

                lesson="Keep successful evolution",

                confidence=0.95,

                learning=False

            )


        else:

            record = LearningRecord(

                strategy=strategy,

                lesson="Improve failed evolution",

                confidence=0.85,

                learning=True

            )


        self.memory.store(
            record
        )


        return {

            "stored": True,

            "lesson": record.lesson,

            "confidence": record.confidence

        }



def test_successful_evolution_updates_learning_memory():


    memory = EvolutionLearningMemory()


    feedback = EvolutionLearningFeedback(
        memory
    )


    result = feedback.process(

        "strategy_v5",

        {

            "success": True

        }

    )


    assert result["stored"] is True


    records = memory.find_by_strategy(
        "strategy_v5"
    )


    assert len(records) == 1


    assert (
        records[0].lesson
        ==
        "Keep successful evolution"
    )


    assert records[0].confidence == 0.95



def test_failed_evolution_creates_learning_signal():


    memory = EvolutionLearningMemory()


    feedback = EvolutionLearningFeedback(
        memory
    )


    result = feedback.process(

        "strategy_v6",

        {

            "success": False

        }

    )


    records = memory.find_by_strategy(
        "strategy_v6"
    )


    assert len(records) == 1


    assert (
        records[0].learning
        is True
    )


    assert (
        records[0].lesson
        ==
        "Improve failed evolution"
    )



def test_feedback_can_be_used_for_future_learning():


    memory = EvolutionLearningMemory()


    feedback = EvolutionLearningFeedback(
        memory
    )


    feedback.process(

        "strategy_v7",

        {

            "success": False

        }

    )


    previous = memory.find_by_strategy(
        "strategy_v7"
    )


    assert len(previous) == 1


    assert (
        previous[0].confidence
        ==
        0.85
    )