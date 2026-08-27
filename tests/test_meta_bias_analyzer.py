from intelligence.meta.meta_bias_analyzer import (
    MetaBiasAnalyzer
)

from intelligence.meta.meta_insight import (
    MetaInsight
)



def test_detects_overconfidence_bias():

    insight = MetaInsight(
        samples=100,
        average_quality=40,
        confidence_accuracy=30
    )


    result = MetaBiasAnalyzer().detect(
        insight
    )


    assert result["bias"] == (
        "OVERCONFIDENT"
    )

    assert result["adjustment"] < 0



def test_detects_underconfidence_bias():

    insight = MetaInsight(
        samples=100,
        average_quality=90,
        confidence_accuracy=30
    )


    result = MetaBiasAnalyzer().detect(
        insight
    )


    assert result["bias"] == (
        "UNDERCONFIDENT"
    )

    assert result["adjustment"] > 0