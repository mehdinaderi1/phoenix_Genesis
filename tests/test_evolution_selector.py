from datetime import datetime, timezone


from intelligence.evolution.evolution_ranker import (
    EvolutionRanker
)

from intelligence.evolution.evolution_selector import (
    EvolutionSelector
)

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)



def test_select_best_lineage():


    weak = [

        EvolutionRecord(

            parent="a_v1",

            child="a_v2",

            generation=2,

            reason="test",

            score_before=90,

            score_after=92,

            timestamp=datetime.now(timezone.utc)

        )

    ]


    strong = [

        EvolutionRecord(

            parent="b_v1",

            child="b_v2",

            generation=2,

            reason="test",

            score_before=70,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )

    ]



    selector = EvolutionSelector(
        EvolutionRanker()
    )


    result = selector.select(

        [

            weak,

            strong

        ]

    )


    assert result is not None

    assert result["analysis"]["score"] == 20