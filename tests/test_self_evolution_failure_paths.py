from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)


class MockEvolutionEngine:

    def __init__(self, evolved=True):
        self.evolved = evolved

    def evolve(self, strategy, score):

        if not self.evolved:
            return {
                "evolved": False,
                "strategy": strategy
            }

        return {
            "evolved": True,
            "strategy": "strategy_v2",
            "generation": 2,
            "score": score + 10
        }


class MockDecision:

    def __init__(self, decision="ACCEPT"):
        self.result = decision

    def decide(self, new_score, parent_score):

        return {
            "decision": self.result
        }


class MockRollback:

    def rollback(self, strategy):

        return {
            "rolled_back": True
        }


class MockGovernance:

    def __init__(self, approved=False):
        self.approved = approved

    def evaluate(self, strategy):

        return {
            "approved": self.approved
        }


class MockIntelligence:

    def __init__(self, decision="ALLOW"):
        self.decision = decision

    def evaluate(self, strategy):

        return {
            "decision": self.decision
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


class MockRecall:

    def analyze(self, strategy):

        return {
            "known": True
        }


def create_controller(
    evolution_engine=None,
    decision=None,
    governance=None,
    intelligence=None
):

    return SelfEvolutionController(

        evolution_engine=evolution_engine
        or MockEvolutionEngine(),

        analytics=None,

        decision=decision
        or MockDecision(),

        rollback=MockRollback(),

        history=MockHistory(),

        recall=MockRecall(),

        intelligence=intelligence
        or MockIntelligence(),

        governance_bridge=governance,

        memory=MockMemory()

    )


def test_governance_reject_blocks_evolution():

    controller = create_controller(
        governance=MockGovernance(False)
    )

    result = controller.run(
        {"name": "strategy_v1"},
        80
    )

    assert result["action"] == "BLOCKED"

    assert (
        result["reason"]
        ==
        "Evolution rejected by governance"
    )


def test_intelligence_block_stops_flow():

    controller = create_controller(
        intelligence=MockIntelligence(
            "BLOCK"
        )
    )

    result = controller.run(
        {"name": "strategy_v1"},
        80
    )

    assert result["action"] == "BLOCKED"

    assert result["reason"] == "BLOCK"


def test_no_evolution_path():

    controller = create_controller(
        evolution_engine=MockEvolutionEngine(
            evolved=False
        )
    )

    result = controller.run(
        {"name": "strategy_v1"},
        40
    )

    assert result["action"] == "NO_EVOLUTION"


def test_rollback_path():

    controller = create_controller(
        decision=MockDecision(
            "ROLLBACK"
        )
    )

    result = controller.run(
        {"name": "strategy_v1"},
        80
    )

    assert result["action"] == "ROLLBACK"

    assert result["rollback"]["rolled_back"] is True