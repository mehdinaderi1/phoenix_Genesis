from intelligence.pattern_analyzer import PatternAnalyzer
from intelligence.decision_record import DecisionRecord



def test_pattern_analyzer():


    records = [

        DecisionRecord(

            symbol="BTCUSDT",

            timeframe="Multi",

            regime="TRENDING_BULLISH",

            signal="BUY",

            confidence=85,

            risk="LOW",

            action="PREPARE_LONG",

            validation_status="APPROVED",

            quality_score=100

        ),


        DecisionRecord(

            symbol="BTCUSDT",

            timeframe="Multi",

            regime="TRENDING_BULLISH",

            signal="BUY",

            confidence=80,

            risk="LOW",

            action="PREPARE_LONG",

            validation_status="APPROVED",

            quality_score=80

        )

    ]



    analyzer = PatternAnalyzer()


    result = analyzer.analyze(records)



    assert len(result) == 1


    assert result[0].regime == "TRENDING_BULLISH"


    assert result[0].action == "PREPARE_LONG"


    assert result[0].samples == 2


    assert result[0].average_quality == 90