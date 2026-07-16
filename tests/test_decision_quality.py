from intelligence.decision_quality import DecisionQualityAnalyzer
from intelligence.decision_record import DecisionRecord



def test_decision_quality():


    record = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="Multi",

        regime="TRENDING",

        signal="BUY",

        confidence=85,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED"

    )


    analyzer = DecisionQualityAnalyzer()


    result = analyzer.calculate(record)


    assert result["quality_score"] == 100

    assert result["action"] == "PREPARE_LONG"