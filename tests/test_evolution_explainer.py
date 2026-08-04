from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionRecord
)


from intelligence.evolution.evolution_explainer import (
    EvolutionExplainer
)



def test_evolution_explainer_success():


    record = EvolutionRecord(

        parent="trend_v1",

        child="trend_v2",

        generation=2,

        reason="performance",

        score_before=70,

        score_after=90,

        timestamp=datetime.now(timezone.utc)

    )


    explainer = EvolutionExplainer()


    result = explainer.explain(
        record
    )


    assert result["strategy_change"] == (
        "trend_v1 -> trend_v2"
    )


    assert result["improvement"] == 20