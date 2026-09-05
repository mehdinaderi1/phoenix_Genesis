from intelligence.meta.meta_learning_engine import MetaLearningEngine
from intelligence.meta.meta_insight import MetaInsight


def test_meta_learning_engine_applies_bias_correction():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.bias = {
        "bias": "OVERCONFIDENT",
        "adjustment": -10
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == -5


def test_meta_learning_engine_applies_underconfidence_correction():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.bias = {
        "bias": "UNDERCONFIDENT",
        "adjustment": 5
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 10


def test_meta_learning_engine_normal_bias_keeps_baseline():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.bias = {
        "bias": "NORMAL",
        "adjustment": 0
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 5
from intelligence.meta.meta_learning_engine import MetaLearningEngine
from intelligence.meta.meta_insight import MetaInsight


def test_meta_learning_ignores_bias_with_insufficient_samples():

    insight = MetaInsight(
        samples=9,
        reliability="HIGH"
    )

    insight.bias = {
        "bias": "OVERCONFIDENT",
        "adjustment": -10
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 0
