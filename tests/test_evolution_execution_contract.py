from intelligence.evolution.evolution_history import (
    EvolutionHistory,
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)


class DummyAnalytics:
    pass


class DummyDecision:

    def decide(self, new_score, old_score):
        return {
            "decision": "KEEP"
        }


class DummyRollback:

    def rollback(self, strategy):
        return strategy


def test_evolution_engine_uses_shared_history():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine(
        history=history
    )

    assert engine.history is history


def test_successful_evolution_records_exactly_one_history_entry():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine(
        history=history
    )

    result = engine.evolve(
        {
            "name": "strategy_a",
            "generation": 1,
        },
        70,
    )

    records = history.all()

    assert result["evolved"] is True
    assert len(records) == 1

    record = records[0]

    assert record.parent == "strategy_a"
    assert record.child == "strategy_a_v2"
    assert record.generation == 2
    assert record.score_before == 70
    assert record.score_after == 80


def test_non_evolution_does_not_write_history():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine(
        history=history
    )

    result = engine.evolve(
        {
            "name": "strategy_a",
            "generation": 1,
        },
        60,
    )

    assert result["evolved"] is False
    assert history.all() == []


def test_controller_does_not_duplicate_engine_history():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine(
        history=history
    )

    controller = SelfEvolutionController(
        evolution_engine=engine,
        analytics=DummyAnalytics(),
        decision=DummyDecision(),
        rollback=DummyRollback(),
        history=history,
    )

    controller.run(
        {
            "name": "trend_v1",
            "generation": 1,
        },
        85,
    )

    assert len(history.all()) == 1