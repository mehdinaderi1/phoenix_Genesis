from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord
)


from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)


from intelligence.evolution.evolution_explainer import (
    EvolutionExplainer
)


from intelligence.evolution.evolution_intelligence_service import (
    EvolutionIntelligenceService
)



def test_intelligence_service_contains_explanation():


    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="performance",

            score_before=70,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )

    )


    service = EvolutionIntelligenceService(

        EvolutionAnalytics(history),

        history,

        EvolutionExplainer()

    )


    report = service.analyze()


    assert report.explanation is not None

    assert report.explanation["improvement"] == 20

    assert report.explanation["strategy_change"] == (
        "trend_v1 -> trend_v2"
    )