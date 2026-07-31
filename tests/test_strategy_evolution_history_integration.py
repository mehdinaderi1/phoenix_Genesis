from intelligence.evolution.evolution_history import EvolutionHistory
from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

def test_evolution_creates_history_record():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine(
        history=history
    )

    strategy = {
        "name": "trend_v1",
        "score": 80,
        "success_rate": 0.8,
        "generation": 1,
    }

    result = engine.evolve(
        "trend_v1",
        80
    )

    assert result["strategy"] == "trend_v1_v2"

    record = history.latest()

    assert record.parent == "trend_v1"
    assert record.child == "trend_v1_v2"
    assert record.generation == 2