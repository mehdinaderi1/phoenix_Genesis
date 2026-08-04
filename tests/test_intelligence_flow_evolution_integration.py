from datetime import datetime, timezone


from intelligence.flow import IntelligenceFlow

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


def test_intelligence_flow_returns_evolution_report():

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


    result = flow.build_report()


    assert "evolution" in result


    assert (
        result["evolution"]["summary"]["best_strategy"]
        ==
        "trend_v2"
    )


    assert (
        result["evolution"]["ranking"]["rank"]
        ==
        "EXCELLENT"
    )