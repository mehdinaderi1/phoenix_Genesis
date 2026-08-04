from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord
)


from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)


from intelligence.evolution.evolution_intelligence_service import (
    EvolutionIntelligenceService
)



def test_evolution_intelligence_analysis():


    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="A",

            child="B",

            generation=2,

            reason="upgrade",

            score_before=70,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )

    )


    service = EvolutionIntelligenceService(

        EvolutionAnalytics(history),

        history

    )


    report = service.analyze()


    assert report.total_evolutions == 1

    assert report.best_strategy == "B"

    assert report.average_improvement == 20

    assert report.success_rate == 100