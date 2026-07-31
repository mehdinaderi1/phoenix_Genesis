from datetime import datetime, timezone


from intelligence.evolution.evolution_ranker import (
    EvolutionRanker
)


from intelligence.evolution.evolution_history import (
    EvolutionRecord
)



def test_evolution_ranker_success():

    records = [

        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="performance",

            score_before=80,

            score_after=95,

            timestamp=datetime.now(timezone.utc)

        )

    ]


    ranker = EvolutionRanker()


    result = ranker.rank(
        records
    )


    assert result["rank"] == "EXCELLENT"

    assert result["evolutions"] == 1