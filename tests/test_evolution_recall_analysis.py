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



def test_recall_analyzer_detects_successful_evolution():


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


    result = analyzer.analyze(
        "trend_v1"
    )


    assert result["history_found"] is True

    assert result["generations"] == 1

    assert result["success_rate"] == 1

    assert result["recommendation"] == "EVOLVE"



def test_new_strategy_has_no_history():


    history = EvolutionHistory()


    recall = EvolutionRecall(
        history
    )


    analyzer = EvolutionRecallAnalyzer(
        recall
    )


    result = analyzer.analyze(
        "new_strategy"
    )


    assert result["history_found"] is False

    assert result["recommendation"] == "NEW"