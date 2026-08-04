from intelligence.learning.self_improvement import SelfImprovement
from intelligence.learning.strategy_optimizer import StrategyOptimizer
from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.performance_record import PerformanceRecord


def test_strategy_performance_knowledge_persistence():

    performances = [
        PerformanceRecord(
            strategy="Trend",
            profit_loss=10,
            success=True
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=20,
            success=True
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-5,
            success=False
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=15,
            success=True
        ),
    ]


    report = SelfImprovement().analyze(
        performances
    )


    score = StrategyOptimizer().optimize(
        "Trend",
        70,
        report
    )


    memory = StrategyMemory()

    updater = StrategyUpdate(
        memory
    )


    updater.update(
        score
    )


    record = memory.latest()


    assert record["strategy"] == "Trend"
    assert record["score"] == 75

    assert record["samples"] == 4
    assert record["success_rate"] == 75