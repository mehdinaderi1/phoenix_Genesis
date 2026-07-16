from intelligence.adaptive_confidence import AdaptiveConfidence


class LearningInsight:

    reliability = "MEDIUM"



def test_adaptive_confidence_uses_experience_bonus():

    engine = AdaptiveConfidence()

    result = engine.adjust(
        60,
        LearningInsight(),
        experience_bonus=8
    )

    assert result == 73