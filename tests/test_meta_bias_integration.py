from intelligence.meta.meta_intelligence import (
    MetaIntelligence
)

from intelligence.decision_record import (
    DecisionRecord
)



def test_meta_intelligence_returns_bias():


    records = [

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="1H",
            regime="TREND",
            signal="BUY",
            confidence=90,
            risk="LOW",
            action="LONG",
            validation_status="REJECTED",
            quality_score=40
        ),


        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="1H",
            regime="TREND",
            signal="BUY",
            confidence=85,
            risk="LOW",
            action="LONG",
            validation_status="REJECTED",
            quality_score=30
        )

    ]


    result = MetaIntelligence().analyze(
        records
    )


    assert result is not None

    assert result["bias"]["bias"] == (
        "OVERCONFIDENT"
    )

    assert result["bias"]["adjustment"] < 0