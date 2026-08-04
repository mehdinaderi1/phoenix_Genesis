from datetime import datetime, timezone


from intelligence.flow import IntelligenceFlow

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)



def test_full_report_contains_evolution_section():

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


    report = flow.create_report(
        None
    )


    assert "evolution" in report


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