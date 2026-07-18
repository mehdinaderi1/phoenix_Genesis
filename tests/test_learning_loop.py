from intelligence.performance_record import PerformanceRecord

from intelligence.learning.self_improvement import SelfImprovement

from intelligence.learning.strategy_optimizer import StrategyOptimizer

from intelligence.learning.strategy_update import StrategyUpdate

from intelligence.strategy_memory import StrategyMemory

from intelligence.strategy_recall import StrategyRecall



def test_learning_loop_end_to_end():

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


    improvement = SelfImprovement().analyze(
        records
    )


    result = StrategyOptimizer().optimize(
        "Trend",
        70,
        improvement
    )


    memory = StrategyMemory()


    updater = StrategyUpdate(
        memory
    )


    updater.update(
        result
    )


    recall = StrategyRecall(
        memory
    )


    strategies = recall.strategy_memory.records


    assert len(strategies) == 1

    assert strategies[0]["strategy"] == "Trend"

    assert strategies[0]["score"] == 75