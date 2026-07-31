from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


from intelligence.evolution.evolution_recall import (
    EvolutionRecall,
)


from intelligence.evolution.evolution_recall_analyzer import (
    EvolutionRecallAnalyzer,
)


from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence,
)



def test_successful_history_allows_evolution():


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


    recall = EvolutionRecall(
        history
    )


    analyzer = EvolutionRecallAnalyzer(
        recall
    )


    intelligence = EvolutionIntelligence(
        analyzer
    )


    result = intelligence.evaluate(
        "trend_v1"
    )


    assert result["decision"] == "ALLOW"



def test_unknown_strategy_is_new():


    history = EvolutionHistory()


    recall = EvolutionRecall(
        history
    )


    analyzer = EvolutionRecallAnalyzer(
        recall
    )


    intelligence = EvolutionIntelligence(
        analyzer
    )


    result = intelligence.evaluate(
        "unknown"
    )


    assert result["decision"] == "NEW"