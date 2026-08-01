from intelligence.lifecycle.lifecycle_evolution_controller import (
    LifecycleEvolutionController,
)


class MockStrategy:
    def __init__(self):
        self.version = "strategy_v1"
        self.name = "strategy"


class MockDecision:
    def __init__(self, action):
        self.action = action


class MockImprovementEngine:

    def __init__(self):
        self.called = False

    def improve(self, strategy):
        self.called = True

        improved = MockStrategy()
        improved.version = "strategy_improved"

        return improved


class MockEvolutionEngine:

    def __init__(self):
        self.called = False

    def evolve(self, strategy):
        self.called = True

        evolved = MockStrategy()
        evolved.version = "strategy_v2"

        return evolved


class MockEvaluator:

    def __init__(self):
        self.called = False

    def evaluate(self, strategy):
        self.called = True
        return "Evaluation completed"


class MockStrategyMemory:

    def __init__(self):
        self.storage = []

    def store(self, strategy):
        self.storage.append(strategy)


def create_controller():

    return LifecycleEvolutionController(
        improvement_engine=MockImprovementEngine(),
        evolution_engine=MockEvolutionEngine(),
        evaluator=MockEvaluator(),
        strategy_memory=MockStrategyMemory(),
    )


def test_lifecycle_keep_action():

    controller = create_controller()

    strategy = MockStrategy()

    result = controller.execute(
        MockDecision("KEEP"),
        strategy
    )

    assert result.executed is True
    assert result.action == "KEEP"
    assert result.strategy_version == "strategy_v1"


def test_lifecycle_improve_triggers_evolution():

    controller = create_controller()

    strategy = MockStrategy()

    result = controller.execute(
        MockDecision("IMPROVE"),
        strategy
    )

    assert result.executed is True
    assert result.action == "IMPROVE"
    assert result.strategy_version == "strategy_v2"


def test_lifecycle_archive_stores_strategy():

    controller = create_controller()

    strategy = MockStrategy()

    result = controller.execute(
        MockDecision("ARCHIVE"),
        strategy
    )

    assert result.executed is True
    assert result.action == "ARCHIVE"

    assert len(
        controller.strategy_memory.storage
    ) == 1


def test_lifecycle_evaluate_runs_evaluator():

    controller = create_controller()

    strategy = MockStrategy()

    result = controller.execute(
        MockDecision("EVALUATE"),
        strategy
    )

    assert result.executed is True
    assert result.action == "EVALUATE"
    assert result.result == "Evaluation completed"


def test_lifecycle_unknown_action():

    controller = create_controller()

    strategy = MockStrategy()

    result = controller.execute(
        MockDecision("UNKNOWN"),
        strategy
    )

    assert result.executed is False
    assert result.result == "Unknown lifecycle action"