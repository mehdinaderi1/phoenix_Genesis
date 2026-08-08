from intelligence.adaptive_intelligence import AdaptiveIntelligence
from intelligence.adaptive_confidence import AdaptiveConfidence
from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster


class DummyLearningInsight:

    reliability = "HIGH"



def test_adaptive_intelligence_combines_learning_and_strategy_experience():

    adaptive_intelligence = AdaptiveIntelligence(
        adaptive_confidence=AdaptiveConfidence(),
        experience_confidence=ExperienceConfidence(),
        confidence_adjuster=ConfidenceAdjuster()
    )


    learning_insight = DummyLearningInsight()


    experience_context = {
        "total_experiences": 10,
        "successful": 8
    }


    confidence = (
        adaptive_intelligence.adjust_analysis_confidence(
            70,
            learning_insight,
            experience_context
        )
    )


    assert confidence > 70