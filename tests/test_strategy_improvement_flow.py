from intelligence.strategy_memory import StrategyMemory

from intelligence.learning.strategy_update import StrategyUpdate

from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)

from intelligence.performance_record import PerformanceRecord



def test_strategy_improvement_updates_memory():

    memory = StrategyMemory()

    updater = StrategyUpdate(
        memory
    )


    engine = StrategyImprovementEngine()


    records = [

        PerformanceRecord(
            strategy="Trend",
            profit_loss=5,
            success=True
        ),

        PerformanceRecord(
            strategy="Trend",
            profit_loss=3,
            success=True
        ),

        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False
        )

    ]


    improved = engine.improve(
        "Trend",
        70,
        records
    )


    updater.update(
        improved
    )


    assert memory.count() == 1


    record = memory.latest()


    assert record["strategy"] == "Trend"

    assert record["score"] == 75