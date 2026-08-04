from datetime import datetime, timezone


from intelligence.flow import IntelligenceFlow

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics,
)

from intelligence.evolution.evolution_ranker import (
    EvolutionRanker,
)

from intelligence.evolution.evolution_explainer import (
    EvolutionExplainer,
)

from intelligence.evolution.evolution_report_builder import (
    EvolutionReportBuilder,
)



def test_intelligence_flow_contains_evolution_report():

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


    report_builder = EvolutionReportBuilder(

        EvolutionAnalytics(history),

        EvolutionRanker(),

        EvolutionExplainer()

    )


    evolution_report = report_builder.build()


    assert evolution_report["summary"]["best_strategy"] == "trend_v2"

    assert evolution_report["ranking"]["rank"] == "EXCELLENT"

    assert (
        evolution_report["explanation"]["status"]
        ==
        "improved"
    )