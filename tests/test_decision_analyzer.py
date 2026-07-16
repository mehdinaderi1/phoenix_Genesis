from intelligence.decision_analyzer import DecisionAnalyzer
from intelligence.decision_record import DecisionRecord


def test_decision_analyzer():

    records = [

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="TRENDING",
            signal="BUY",
            confidence=85,
            risk="LOW",
            action="PREPARE_LONG",
            validation_status="APPROVED"
        ),

        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="SIDEWAYS",
            signal="SELL",
            confidence=60,
            risk="MEDIUM",
            action="WAIT",
            validation_status="REJECTED"
        )
    ]


    analyzer = DecisionAnalyzer()

    result = analyzer.analyze(records)


    assert result["total_decisions"] == 2
    assert result["approved"] == 1
    assert result["rejected"] == 1
    assert result["average_confidence"] == 72.5