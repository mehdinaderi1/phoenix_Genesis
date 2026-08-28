from intelligence.meta.meta_insight import (
    MetaInsight
)


def test_meta_insight_contains_meta_feedback():

    insight = MetaInsight(
        samples=1,
        average_quality=95,
        confidence_accuracy=100,
        reliability="HIGH"
    )


    assert hasattr(
        insight,
        "meta_feedback"
    )


    assert (
        insight.meta_feedback
        is None
    )