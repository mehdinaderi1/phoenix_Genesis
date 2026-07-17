from intelligence.confidence_adjuster import ConfidenceAdjuster



def test_confidence_adjustment_positive():

    adjuster = ConfidenceAdjuster()


    result = adjuster.adjust(
        72,
        6
    )


    assert result == 78



def test_confidence_adjustment_limit():

    adjuster = ConfidenceAdjuster()


    result = adjuster.adjust(
        98,
        10
    )


    assert result == 100