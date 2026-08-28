from intelligence.meta.meta_learning_engine import (
    MetaLearningEngine
)

from intelligence.meta.meta_insight import (
    MetaInsight
)


def test_meta_learning_engine_high_reliability_adjusts_confidence():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    result = (
        MetaLearningEngine()
        .learn(insight)
    )

    assert result["confidence_adjustment"] == 5

    assert result["reliability"] == "HIGH"


def test_meta_learning_engine_low_reliability_adjusts_confidence():

    insight = MetaInsight(
        samples=10,
        reliability="LOW"
    )

    result = (
        MetaLearningEngine()
        .learn(insight)
    )

    assert result["confidence_adjustment"] == -5

    assert result["reliability"] == "LOW"


def test_meta_learning_engine_requires_enough_samples():

    insight = MetaInsight(
        samples=9,
        reliability="HIGH"
    )

    result = (
        MetaLearningEngine()
        .learn(insight)
    )

    assert result["confidence_adjustment"] == 0