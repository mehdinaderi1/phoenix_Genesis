from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


from intelligence.evolution.evolution_recall import (
    EvolutionRecall,
)



def test_recall_strategy_lineage():


    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="upgrade",

            score_before=80,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )
    )


    history.add(

        EvolutionRecord(

            parent="trend_v2",

            child="trend_v3",

            generation=3,

            reason="upgrade",

            score_before=90,

            score_after=95,

            timestamp=datetime.now(timezone.utc)

        )
    )



    recall = EvolutionRecall(
        history
    )


    lineage = recall.find_lineage(
        "trend_v2"
    )


    assert len(lineage) == 2



def test_generation_count():


    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="alpha",

            child="alpha_v2",

            generation=2,

            reason="evolution",

            score_before=70,

            score_after=80,

            timestamp=datetime.now(timezone.utc)

        )
    )


    recall = EvolutionRecall(
        history
    )


    assert recall.generations(
        "alpha"
    ) == 1