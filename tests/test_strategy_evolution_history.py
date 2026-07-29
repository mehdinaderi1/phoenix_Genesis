from intelligence.learning.strategy_evolution_history import (
    StrategyEvolutionHistory,
    EvolutionRecord
)


def test_store_record():

    history = StrategyEvolutionHistory()

    history.add(

        EvolutionRecord(

            strategy="Trend_v2",

            parent="Trend",

            generation=2,

            decision="IMPROVE",

            reason="Low success",

            score=65,

            success_rate=0.55
        )
    )

    assert len(history.all()) == 1


def test_latest_record():

    history = StrategyEvolutionHistory()

    history.add(

        EvolutionRecord(

            strategy="Trend",

            parent=None,

            generation=1,

            decision="KEEP",

            reason="Stable",

            score=90,

            success_rate=0.92
        )
    )

    assert history.latest().strategy == "Trend"