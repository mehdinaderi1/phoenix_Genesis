from intelligence.meta.meta_learning_engine import MetaLearningEngine
from intelligence.meta.meta_insight import MetaInsight


def test_meta_learning_feedback_high_reliability():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.meta_feedback = {
        "samples": 10,
        "successful_adjustments": 8,
        "success_rate": 0.8,
        "reliability": "HIGH"
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 5
    assert result["learning_reliability"] == "HIGH"


def test_meta_learning_feedback_medium_reliability():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.meta_feedback = {
        "samples": 10,
        "successful_adjustments": 5,
        "success_rate": 0.5,
        "reliability": "MEDIUM"
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 5
    assert result["learning_reliability"] == "MEDIUM"


def test_meta_learning_feedback_low_reliability():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    insight.meta_feedback = {
        "samples": 10,
        "successful_adjustments": 2,
        "success_rate": 0.2,
        "reliability": "LOW"
    }

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 5
    assert result["learning_reliability"] == "LOW"


def test_meta_learning_without_feedback_has_unknown_learning_reliability():

    insight = MetaInsight(
        samples=10,
        reliability="HIGH"
    )

    result = MetaLearningEngine().learn(insight)

    assert result["confidence_adjustment"] == 5
    assert result["learning_reliability"] == "UNKNOWN"
