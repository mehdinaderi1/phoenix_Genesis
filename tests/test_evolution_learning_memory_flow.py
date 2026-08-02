from dataclasses import dataclass


@dataclass
class LearningRecord:

    strategy: str
    lesson: str
    confidence: float
    learning: bool



class MockLearningMemory:

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



class MockLearningBridge:

    def __init__(
        self,
        memory
    ):

        self.memory = memory


    def evaluate(
        self,
        old_strategy,
        new_strategy,
        performance
    ):

        if performance["success_rate"] < 0.5:

            record = LearningRecord(

                strategy=new_strategy,

                lesson="Improve entry conditions",

                confidence=0.9,

                learning=True

            )


            self.memory.store(record)


            return {

                "learning": True,

                "confidence": 0.9,

                "lesson": record.lesson

            }


        record = LearningRecord(

            strategy=new_strategy,

            lesson="Stable strategy",

            confidence=0.95,

            learning=False

        )


        self.memory.store(record)


        return {

            "learning": False,

            "confidence": 0.95,

            "lesson": record.lesson

        }



def test_learning_bridge_stores_failed_evolution_lesson():

    memory = MockLearningMemory()


    bridge = MockLearningBridge(
        memory
    )


    result = bridge.evaluate(

        "strategy_v1",

        "strategy_v2",

        {

            "score": 40,

            "success_rate": 0.3

        }

    )


    assert result["learning"] is True


    lessons = memory.find_by_strategy(
        "strategy_v2"
    )


    assert len(lessons) == 1


    assert (
        lessons[0].lesson
        ==
        "Improve entry conditions"
    )


    assert (
        lessons[0].confidence
        ==
        0.9
    )



def test_learning_bridge_stores_successful_evolution_lesson():

    memory = MockLearningMemory()


    bridge = MockLearningBridge(
        memory
    )


    result = bridge.evaluate(

        "strategy_v1",

        "strategy_v3",

        {

            "score": 95,

            "success_rate": 0.95

        }

    )


    assert result["learning"] is False


    lessons = memory.find_by_strategy(
        "strategy_v3"
    )


    assert len(lessons) == 1


    assert (
        lessons[0].lesson
        ==
        "Stable strategy"
    )


    assert (
        lessons[0].confidence
        ==
        0.95
    )



def test_learning_memory_can_recall_previous_lesson():

    memory = MockLearningMemory()


    memory.store(

        LearningRecord(

            strategy="strategy_v4",

            lesson="Optimize parameters",

            confidence=0.85,

            learning=True

        )

    )


    recalled = memory.find_by_strategy(
        "strategy_v4"
    )


    assert len(recalled) == 1


    assert (
        recalled[0].lesson
        ==
        "Optimize parameters"
    )