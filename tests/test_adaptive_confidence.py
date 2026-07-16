from intelligence.adaptive_confidence import AdaptiveConfidence



class MockInsight:

    def __init__(self, reliability):

        self.reliability = reliability



def test_adaptive_confidence_high_reliability():

    engine = AdaptiveConfidence()


    result = engine.adjust(
        80,
        MockInsight("HIGH")
    )


    assert result == 90



def test_adaptive_confidence_low_reliability():

    engine = AdaptiveConfidence()


    result = engine.adjust(
        80,
        MockInsight("LOW")
    )


    assert result == 70



def test_adaptive_confidence_limit():

    engine = AdaptiveConfidence()


    result = engine.adjust(
        95,
        MockInsight("HIGH")
    )


    assert result == 100