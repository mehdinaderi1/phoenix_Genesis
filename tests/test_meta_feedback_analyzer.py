from intelligence.meta.meta_feedback import (
    MetaFeedbackRecord
)

from intelligence.meta.meta_feedback_analyzer import (
    MetaFeedbackAnalyzer
)



def test_meta_feedback_analyzer_detects_reliable_learning():

    records = [

        MetaFeedbackRecord(
            confidence_before=90,
            adjustment=-10,
            confidence_after=80,
            outcome="SUCCESS",
            meta_effective=True
        ),

        MetaFeedbackRecord(
            confidence_before=85,
            adjustment=-5,
            confidence_after=80,
            outcome="SUCCESS",
            meta_effective=True
        ),

        MetaFeedbackRecord(
            confidence_before=70,
            adjustment=5,
            confidence_after=75,
            outcome="FAILED",
            meta_effective=False
        )

    ]


    result = (
        MetaFeedbackAnalyzer()
        .analyze(records)
    )


    assert result["samples"] == 3

    assert (
        result["successful_adjustments"]
        == 2
    )

    assert (
        result["reliability"]
        == "HIGH"
    )