from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics,
)



def test_evolution_count():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="A",
            child="B",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=85,
            timestamp=datetime.now(timezone.utc),
        )
    )


    analytics = EvolutionAnalytics(
        history
    )


    assert analytics.count() == 1



def test_best_strategy_evolution():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="A",
            child="B",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=80,
            timestamp=datetime.now(timezone.utc),
        )
    )


    history.add(
        EvolutionRecord(
            parent="B",
            child="C",
            generation=3,
            reason="optimization",
            score_before=80,
            score_after=95,
            timestamp=datetime.now(timezone.utc),
        )
    )


    analytics = EvolutionAnalytics(
        history
    )


    best = analytics.best_child()


    assert best.child == "C"



def test_average_improvement():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="A",
            child="B",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=80,
            timestamp=datetime.now(timezone.utc),
        )
    )


    history.add(
        EvolutionRecord(
            parent="B",
            child="C",
            generation=3,
            reason="upgrade",
            score_before=80,
            score_after=90,
            timestamp=datetime.now(timezone.utc),
        )
    )


    analytics = EvolutionAnalytics(
        history
    )


    assert analytics.average_improvement() == 10