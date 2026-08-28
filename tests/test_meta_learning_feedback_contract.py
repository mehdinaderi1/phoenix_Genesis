from intelligence.meta.meta_learning_engine import (
    MetaLearningEngine
)

from intelligence.meta.meta_insight import (
    MetaInsight
)


def test_meta_learning_engine_receives_meta_feedback():

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

    result = (
        MetaLearningEngine()
        .learn(insight)
    )

    assert result is not None

    assert (
        result["reliability"]
        == "HIGH"
    )