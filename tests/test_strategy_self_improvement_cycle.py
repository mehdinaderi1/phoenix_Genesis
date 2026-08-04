from intelligence.performance_record import PerformanceRecord
from intelligence.learning.self_improvement import SelfImprovement
from intelligence.learning.strategy_optimizer import StrategyOptimizer
from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_update import StrategyUpdate


def test_strategy_self_improvement_cycle():

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


    improvement = SelfImprovement()

    report = improvement.analyze(
        performances
    )


    assert report.total_trades == 4
    assert report.win_rate == 75


    optimizer = StrategyOptimizer()

    score = optimizer.optimize(
        "Trend",
        70,
        report
    )


    assert score.strategy == "Trend"
    assert score.score == 75


    memory = StrategyMemory()

    updater = StrategyUpdate(
        memory
    )


    result = updater.update(
        score
    )


    assert result["updated"] is True

    latest = memory.latest()

    assert latest["strategy"] == "Trend"
    assert latest["score"] == 75

    assert latest["samples"] == 4
    assert latest["success_rate"] == 75