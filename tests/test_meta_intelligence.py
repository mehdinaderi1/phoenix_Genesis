from intelligence.meta.meta_intelligence import MetaIntelligence
from intelligence.decision_record import DecisionRecord


def test_meta_intelligence_detects_high_quality_decisions():

    records = [

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="TREND",
            signal="BUY",
            confidence=90,
            risk="LOW",
            action="LONG",
            validation_status="APPROVED",
            quality_score=100
        ),

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="TREND",
            signal="BUY",
            confidence=85,
            risk="LOW",
            action="LONG",
            validation_status="APPROVED",
            quality_score=90
        )

    ]


    intelligence = MetaIntelligence()


    insight = intelligence.analyze(
        records
    )


    assert insight.samples == 2

    assert insight.average_quality == 95

    assert insight.confidence_accuracy == 100

    assert insight.reliability == "HIGH"