from intelligence.lifecycle.lifecycle_evolution_flow import LifecycleEvolutionFlow


class MockStrategyEvolutionController:

    def __init__(self):
        self.actions = []

    def execute(self, decision, strategy):
        self.actions.append(decision)

        if decision == "IMPROVE":
            return {
                "action": "IMPROVE",
                "strategy": f"{strategy}_v2",
                "status": "EVOLVED"
            }

        if decision == "KEEP":
            return {
                "action": "KEEP",
                "strategy": strategy,
                "status": "RETAINED"
            }

        if decision == "ARCHIVE":
            return {
                "action": "ARCHIVE",
                "strategy": strategy,
                "status": "ARCHIVED"
            }

        if decision == "EVALUATE":
            return {
                "action": "EVALUATE",
                "strategy": strategy,
                "status": "EVALUATED"
            }


class MockLifecycleDecisionEngine:

    def __init__(self, decision):
        self.decision = decision

    def decide(self, strategy):
        return self.decision


class MockLifecycleHistory:

    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)


def build_flow(decision):

    controller = MockStrategyEvolutionController()

    engine = MockLifecycleDecisionEngine(decision)

    history = MockLifecycleHistory()

    flow = LifecycleEvolutionFlow(
        lifecycle_decision_engine=engine,
        evolution_controller=controller,
        lifecycle_history=history
    )

    return flow, controller, history


def test_lifecycle_evolution_flow_improve_creates_new_version():

    flow, controller, history = build_flow("IMPROVE")

    result = flow.execute("Strategy")

    assert result["action"] == "IMPROVE"
    assert result["status"] == "EVOLVED"
    assert result["strategy"] == "Strategy_v2"

    assert controller.actions == ["IMPROVE"]


def test_lifecycle_evolution_flow_keep_retains_version():

    flow, controller, history = build_flow("KEEP")

    result = flow.execute("Strategy")

    assert result["action"] == "KEEP"
    assert result["status"] == "RETAINED"

    assert controller.actions == ["KEEP"]


def test_lifecycle_evolution_flow_archive_strategy():

    flow, controller, history = build_flow("ARCHIVE")

    result = flow.execute("Strategy")

    assert result["action"] == "ARCHIVE"
    assert result["status"] == "ARCHIVED"

    assert controller.actions == ["ARCHIVE"]


def test_lifecycle_evolution_flow_evaluate_strategy():

    flow, controller, history = build_flow("EVALUATE")

    result = flow.execute("Strategy")

    assert result["action"] == "EVALUATE"
    assert result["status"] == "EVALUATED"

    assert controller.actions == ["EVALUATE"]