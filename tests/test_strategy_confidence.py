from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)
from intelligence.performance_record import PerformanceRecord
from intelligence.learning.strategy_update import StrategyUpdate


def test_strategy_self_improvement_end_to_end():

    memory = StrategyMemory()

    memory.store({

        "strategy": "Trend",

        "regime": "BULLISH",

        "signal": "BUY",

        "risk": "LOW",

        "score": 70

    })


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


    improvement = StrategyImprovementEngine()


    improved = improvement.improve(

        "Trend",

        70,

        records

    )


    updater = StrategyUpdate(
        memory
    )


    updater.update(
        improved,
        {
            "regime": "BULLISH",
            "signal": "BUY",
            "risk": "LOW"
        }
    )


    strategies = memory.find_by_pattern(

        "BULLISH",

        "BUY",

        "LOW"

    )


    assert len(strategies) == 2


    updated = strategies[-1]


    assert updated["strategy"] == "Trend"

    assert updated["score"] == 75