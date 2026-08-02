from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def evolve(self, strategy, score):

        return {
            "evolved": True,
            "strategy": "strategy_v2",
            "generation": 2,
            "score": score + 10
        }


class MockDecision:

    def decide(self, new_score, parent_score):

        return {
            "decision": "ACCEPT"
        }


class MockRollback:

    def rollback(self, strategy):

        return {
            "rolled_back": True
        }


class MockGovernance:

    def evaluate(self, strategy):

        return {
            "approved": True
        }


class MockIntelligence:

    def evaluate(self, strategy):

        return {
            "decision": "ALLOW"
        }


class MockRecall:

    def analyze(self, strategy):

        return {
            "known": True
        }


class MockHistory:

    def __init__(self):

        self.records = []


    def add(self, record):

        self.records.append(record)


class MockMemory:

    def __init__(self):

        self.records = []


    def store(self, record):

        self.records.append(record)



def test_evolution_history_and_memory_are_consistent():

    history = MockHistory()

    memory = MockMemory()


    controller = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=None,

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

        recall=MockRecall(),

        intelligence=MockIntelligence(),

        governance_bridge=MockGovernance(),

        memory=memory

    )


    result = controller.run(

        {
            "name": "strategy_v1"
        },

        80

    )


    assert result["action"] == "ACCEPT"


    assert len(history.records) == 1

    assert len(memory.records) == 1


    history_record = history.records[0]

    memory_record = memory.records[0]


    assert (
        history_record.parent
        ==
        memory_record.parent
    )


    assert (
        history_record.child
        ==
        memory_record.child
    )


    assert (
        history_record.generation
        ==
        memory_record.generation
    )


    assert (
        history_record.score_before
        ==
        memory_record.score_before
    )


    assert (
        history_record.score_after
        ==
        memory_record.score_after
    )


def test_evolution_record_keeps_lineage_information():

    history = MockHistory()

    memory = MockMemory()


    controller = SelfEvolutionController(

        evolution_engine=MockEvolutionEngine(),

        analytics=None,

        decision=MockDecision(),

        rollback=MockRollback(),

        history=history,

        recall=MockRecall(),

        intelligence=MockIntelligence(),

        governance_bridge=MockGovernance(),

        memory=memory

    )


    controller.run(

        {
            "name": "scalping_v1"
        },

        90

    )


    record = history.records[0]


    assert record.parent == "scalping_v1"

    assert record.child == "strategy_v2"

    assert record.generation == 2

    assert record.reason == "self evolution"