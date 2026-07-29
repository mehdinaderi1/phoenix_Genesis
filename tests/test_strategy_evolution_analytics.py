from intelligence.learning.strategy_evolution_history import (
    StrategyEvolutionHistory,
    EvolutionRecord
)

from intelligence.learning.strategy_evolution_analytics import (
    StrategyEvolutionAnalytics
)


def test_summary():

    history = StrategyEvolutionHistory()

    history.add(
        EvolutionRecord(
            strategy="A",
            parent=None,
            generation=1,
            decision="KEEP",
            reason="Good",
            score=90,
            success_rate=0.90
        )
    )

    history.add(
        EvolutionRecord(
            strategy="B",
            parent="A",
            generation=2,
            decision="IMPROVE",
            reason="Better",
            score=70,
            success_rate=0.60
        )
    )

    analytics = StrategyEvolutionAnalytics(
        history
    )

    result = analytics.summary()

    assert result["total"] == 2
    assert result["kept"] == 1
    assert result["improved"] == 1
    assert result["average_score"] == 80.0