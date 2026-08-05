from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.learning.strategy_improvement_engine import StrategyImprovementEngine
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_quality_gate import StrategyQualityGate
from intelligence.learning.strategy_history import StrategyHistory
from intelligence.strategy_feedback import StrategyFeedback


def test_strategy_champion_evolves_after_success_feedback():

    memory = StrategyMemory()

    history = StrategyHistory()

    update = StrategyUpdate(
        memory,
        StrategyQualityGate(),
        history
    )


    memory.store(
        {
            "name": "trend_following",
            "strategy": "trend_following",
            "regime": "bullish",
            "signal": "BUY",
            "risk": "LOW",
            "score": 70,
            "success_rate": 0.6,
            "samples": 10,
            "status": "ACTIVE"
        }
    )


    feedback = StrategyFeedback()


    performance = feedback.create_record(
        "trend_following",
        {
            "result": "SUCCESS",
            "score": 100
        }
    )


    engine = StrategyImprovementEngine()


    improved = engine.improve(
        "trend_following",
        70,
        [
            performance
        ]
    )


    result = update.update(
        improved
    )


    assert result["updated"] is True


    recall = StrategyRecall(
        memory
    )


    selector = StrategySelector(
        recall,
        StrategyRanker()
    )


    champion = selector.select(
        "bullish",
        "BUY",
        "LOW"
    )


    assert champion is not None

    assert champion["strategy"] == "trend_following"

    assert champion["score"] >= 75