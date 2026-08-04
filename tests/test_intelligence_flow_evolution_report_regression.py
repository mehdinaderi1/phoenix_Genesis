from datetime import datetime, timezone


from intelligence.flow import IntelligenceFlow

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)



def test_intelligence_flow_keeps_original_report_with_evolution():

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


    flow = IntelligenceFlow()


    flow.evolution_history = history


    report = flow.build_report()


    assert report is not None


    assert "evolution" in report


    assert (
        report["evolution"]["summary"]["total_evolutions"]
        ==
        1
    )


    assert (
        report["evolution"]["summary"]["best_strategy"]
        ==
        "trend_v2"
    )


    assert (
        report["evolution"]["ranking"]["rank"]
        ==
        "EXCELLENT"
    )