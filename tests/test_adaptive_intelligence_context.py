from intelligence.adaptive_intelligence import (
    AdaptiveIntelligence
)

from intelligence.adaptive_confidence import (
    AdaptiveConfidence
)

from intelligence.experience_confidence import (
    ExperienceConfidence
)

from intelligence.confidence_adjuster import (
    ConfidenceAdjuster
)

from intelligence.adaptive_learning_context import (
    AdaptiveLearningContext
)


class DummyLearningInsight:

    reliability = "HIGH"


def test_adaptive_intelligence_adjusts_context_confidence():

    intelligence = AdaptiveIntelligence(

        adaptive_confidence=AdaptiveConfidence(),

        experience_confidence=ExperienceConfidence(),

        confidence_adjuster=ConfidenceAdjuster()

    )


    context = AdaptiveLearningContext(

        base_confidence=70,

        learning_insight=DummyLearningInsight(),

        experience_context={

            "total_experiences": 10,

            "successful": 8

        }

    )


    confidence = (
        intelligence.adjust_context_confidence(
            context
        )
    )


    assert confidence > 70
