from datetime import datetime, timezone


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



def test_evolution_report_builder_success():

    history = EvolutionHistory()


    record = EvolutionRecord(

        parent="trend_v1",

        child="trend_v2",

        generation=2,

        reason="performance",

        score_before=70,

        score_after=90,

        timestamp=datetime.now(timezone.utc)

    )


    history.add(record)


    builder = EvolutionReportBuilder(

        EvolutionAnalytics(history),

        EvolutionRanker(),

        EvolutionExplainer()

    )


    report = builder.build()


    assert report["summary"]["total_evolutions"] == 1

    assert report["summary"]["best_strategy"] == "trend_v2"

    assert report["ranking"]["rank"] == "EXCELLENT"

    assert report["explanation"]["status"] == "improved"