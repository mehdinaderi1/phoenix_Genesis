from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster


def test_strategy_champion_improves_decision_confidence():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "TREND_BUY_LOW",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "score": 90,
            "success_rate": 0.9,
            "samples": 50,
            "status": "ACTIVE"
        }
    )


    selector = StrategySelector(
        StrategyRecall(memory),
        StrategyRanker()
    )


    result = selector.select_with_result(
        "TREND",
        "BUY",
        "LOW"
    )


    assert result is not None


    champion = result["champion"]


    assert champion["strategy"] == (
        "TREND_BUY_LOW"
    )


    bonus = ExperienceConfidence().calculate_from_strategy(
        champion
    )


    confidence = ConfidenceAdjuster().adjust(
        70,
        bonus
    )


    assert bonus > 0

    assert confidence > 70