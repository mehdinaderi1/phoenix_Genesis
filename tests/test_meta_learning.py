from intelligence.meta.meta_learning import (
    MetaLearning
)

from intelligence.meta.meta_insight import (
    MetaInsight
)



def test_meta_learning_reduces_overconfidence():


    insight = MetaInsight(

        samples=100,

        average_quality=40,

        confidence_accuracy=30,

        reliability="LOW",

        bias="OVERCONFIDENT"

    )


    result = MetaLearning().analyze(
        insight
    )


    assert result["recommendation"] == (
        "REDUCE_CONFIDENCE"
    )

    assert result["confidence_adjustment"] < 0



def test_meta_learning_increases_underconfidence():


    insight = MetaInsight(

        samples=100,

        average_quality=90,

        confidence_accuracy=30,

        reliability="HIGH",

        bias="UNDERCONFIDENT"

    )


    result = MetaLearning().analyze(
        insight
    )


    assert result["recommendation"] == (
        "INCREASE_CONFIDENCE"
    )

    assert result["confidence_adjustment"] > 0