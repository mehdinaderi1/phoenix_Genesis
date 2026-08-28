from intelligence.meta.meta_feedback import (
    MetaFeedbackRecord
)

from intelligence.meta.meta_memory import (
    MetaMemory
)

from intelligence.meta.meta_intelligence import (
    MetaIntelligence
)


from intelligence.decision_record import (
    DecisionRecord
)



def test_meta_feedback_flows_into_meta_intelligence():


    decision_records = [

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="1H",
            regime="TREND",
            signal="BUY",
            confidence=90,
            risk="LOW",
            action="LONG",
            validation_status="APPROVED",
            quality_score=95
        )

    ]


    meta_memory = MetaMemory()


    meta_memory.store(

        MetaFeedbackRecord(

            confidence_before=90,

            adjustment=-10,

            confidence_after=80,

            outcome="SUCCESS",

            meta_effective=True

        )

    )


    insight = (
        MetaIntelligence()
        .analyze(
            decision_records,
            meta_memory.get_records()
        )
    )


    assert insight is not None


    assert (
        insight.meta_feedback["samples"]
        == 1
    )


    assert (
        insight.meta_feedback["reliability"]
        == "HIGH"
    )