from intelligence.adaptive_intelligence import AdaptiveIntelligence
from intelligence.adaptive_confidence import AdaptiveConfidence
from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster


def test_adaptive_intelligence_increases_strategy_confidence():

    intelligence = AdaptiveIntelligence(
        adaptive_confidence=AdaptiveConfidence(),
        experience_confidence=ExperienceConfidence(),
        confidence_adjuster=ConfidenceAdjuster()
    )


    strategy = {
        "strategy": "TREND_BUY_LOW",
        "success_rate": 0.9
    }


    confidence = intelligence.adjust_strategy_confidence(
        70,
        strategy
    )


    assert confidence > 70


def test_adaptive_intelligence_decreases_strategy_confidence():

    intelligence = AdaptiveIntelligence(
        adaptive_confidence=AdaptiveConfidence(),
        experience_confidence=ExperienceConfidence(),
        confidence_adjuster=ConfidenceAdjuster()
    )


    strategy = {
        "strategy": "WEAK_STRATEGY",
        "success_rate": 0.1
    }


    confidence = intelligence.adjust_strategy_confidence(
        70,
        strategy
    )


    assert confidence < 70