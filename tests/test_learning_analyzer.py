from intelligence.learning_analyzer import LearningAnalyzer
from intelligence.decision_record import DecisionRecord



def test_learning_analyzer():


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

            quality_score=90

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


    analyzer = LearningAnalyzer()


    result = analyzer.analyze(records)


    assert result.samples == 2

    assert result.average_confidence == 82.5

    assert result.average_quality == 85

    assert result.reliability == "HIGH"