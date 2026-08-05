from intelligence.strategy_feedback import StrategyFeedback
from intelligence.learning.strategy_improvement_engine import StrategyImprovementEngine
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_history import StrategyHistory
from intelligence.learning.strategy_quality_gate import StrategyQualityGate
from intelligence.learning.strategy_ranker import StrategyRanker



def test_strategy_feedback_improves_and_updates_ranking():

    memory = StrategyMemory()

    history = StrategyHistory()

    update = StrategyUpdate(
        memory,
        StrategyQualityGate(),
        history
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
        improved,
        {
            "regime": "bullish",
            "signal": "BUY",
            "risk": "LOW"
        }
    )


    assert result["updated"] is True


    assert memory.count() == 1


    stored = memory.latest()


    assert stored["strategy"] == "trend_following"

    assert stored["score"] >= 70

    assert stored["success_rate"] > 0



def test_updated_strategy_can_be_ranked():

    ranker = StrategyRanker()


    strategies = [

        {
            "strategy": "trend_following",
            "score": 80,
            "success_rate": 0.9,
            "status": "ACTIVE"
        },

        {
            "strategy": "weak_strategy",
            "score": 50,
            "success_rate": 0.3,
            "status": "ACTIVE"
        }

    ]


    ranked = ranker.rank(
        strategies
    )


    assert ranked[0]["strategy"] == "trend_following"