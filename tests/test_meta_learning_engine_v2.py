from intelligence.meta.meta_learning_engine import (
    MetaLearningEngine
)

from intelligence.meta.meta_insight import (
    MetaInsight
)

from types import SimpleNamespace

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


def test_meta_learning_engine_returns_no_data_for_none():

    engine = MetaLearningEngine()

    result = engine.learn(None)

    assert result == {
        "confidence_adjustment": 0,
        "learning": "NO_DATA"
    }


def test_meta_learning_engine_keeps_zero_adjustment_for_unknown_reliability():

    engine = MetaLearningEngine()

    insight = SimpleNamespace(
        reliability="UNKNOWN",
        samples=20
    )

    result = engine.learn(insight)

    assert result["confidence_adjustment"] == 0
    assert result["reliability"] == "UNKNOWN"