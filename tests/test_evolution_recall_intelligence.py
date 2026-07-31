from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord
)

from intelligence.evolution.evolution_recall import (
    EvolutionRecall
)

from intelligence.evolution.evolution_recall_intelligence import (
    EvolutionRecallIntelligence
)

from datetime import datetime, timezone



def test_recall_intelligence_detects_success():


    history = EvolutionHistory()


    history.add(
        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="performance",

            score_before=80,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )
    )


    recall = EvolutionRecall(
        history
    )


    intelligence = EvolutionRecallIntelligence(
        recall
    )


    result = intelligence.analyze(
        "trend_v1"
    )


    assert result["known"] is True

    assert result["evolution_count"] == 1

    assert result["confidence"] == 100