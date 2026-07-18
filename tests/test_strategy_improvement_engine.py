from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)

from intelligence.performance_record import PerformanceRecord



def test_strategy_improvement_engine():

    records = [

        PerformanceRecord(
            strategy="Trend",
            profit_loss=3,
            success=True
        ),

        PerformanceRecord(
            strategy="Trend",
            profit_loss=2,
            success=True
        ),

        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False
        )

    ]


    result = StrategyImprovementEngine().improve(
        "Trend",
        70,
        records
    )


    assert result.score == 75

    assert result.strategy == "Trend"