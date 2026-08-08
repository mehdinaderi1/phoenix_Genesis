from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster


def test_strategy_performance_improves_confidence():

    strategy = {
        "strategy": "TREND_BUY_LOW",
        "score": 90,
        "success_rate": 0.9,
        "samples": 50,
        "status": "ACTIVE"
    }


    experience = ExperienceConfidence()

    bonus = experience.calculate_from_strategy(
        strategy
    )


    assert bonus > 0


    adjuster = ConfidenceAdjuster()


    confidence = adjuster.adjust(
        70,
        bonus
    )


    assert confidence > 70