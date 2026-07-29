from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight
)

from intelligence.learning.strategy_evolution_history import (
    StrategyEvolutionHistory,
    EvolutionRecord
)

from intelligence.learning.strategy_evolution_analytics import (
    StrategyEvolutionAnalytics
)


def test_strategy_evolution_full_pipeline():

    strategy = {

        "name": "Trend",

        "score": 65,

        "success_rate": 0.60

    }


    engine = StrategyEvolutionEngine()


    decision = engine.evaluate(
        strategy
    )


    assert decision["decision"] == "IMPROVE"



    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        strategy,

        {
            "name": "Trend_v2"
        },

        {

            "score": 65,

            "success_rate": 0.60

        },

        decision["decision"]

    )


    assert insight.learning is True



    history = StrategyEvolutionHistory()


    history.add(

        EvolutionRecord(

            strategy="Trend_v2",

            parent="Trend",

            generation=2,

            decision=decision["decision"],

            reason=insight.reason,

            score=65,

            success_rate=0.60

        )

    )


    assert history.latest() is not None

    assert history.latest().decision == "IMPROVE"



    analytics = StrategyEvolutionAnalytics(

        history

    )


    result = analytics.summary()


    assert result["total"] == 1

    assert result["improved"] == 1

    assert result["average_score"] == 65.0

    assert result["average_success_rate"] == 0.60