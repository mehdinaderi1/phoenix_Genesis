from intelligence.evolution.evolution_lineage import (
    EvolutionLineage
)

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)

from datetime import datetime, timezone



def create_record(
    parent,
    child,
    generation
):

    return EvolutionRecord(

        parent=parent,

        child=child,

        generation=generation,

        reason="performance",

        score_before=80,

        score_after=90,

        timestamp=datetime.now(
            timezone.utc
        )
    )



def test_evolution_lineage_tree():

    lineage = EvolutionLineage()


    lineage.add(
        create_record(
            "trend_v1",
            "trend_v2",
            2
        )
    )


    lineage.add(
        create_record(
            "trend_v2",
            "trend_v3",
            3
        )
    )


    result = lineage.find_lineage(
        "trend_v3"
    )


    assert len(result) == 2

    assert result[0].child == "trend_v2"

    assert result[1].child == "trend_v3"



def test_lineage_children():

    lineage = EvolutionLineage()


    lineage.add(
        create_record(
            "trend_v1",
            "trend_v2",
            2
        )
    )


    children = lineage.children(
        "trend_v1"
    )


    assert len(children) == 1

    assert children[0].child == "trend_v2"