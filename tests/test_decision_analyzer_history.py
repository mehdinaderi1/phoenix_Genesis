from intelligence.decision_analyzer import DecisionAnalyzer
from intelligence.decision_history import DecisionHistory
from intelligence.decision_record import DecisionRecord



def test_decision_analyzer_history():


    history = DecisionHistory()


    history.add(
        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="TRENDING",
            signal="BUY",
            confidence=90,
            risk="LOW",
            action="PREPARE_LONG",
            validation_status="APPROVED"
        )
    )


    history.add(
        DecisionRecord(
            symbol="BTCUSDT",
            timeframe="Multi",
            regime="SIDEWAYS",
            signal="SELL",
            confidence=50,
            risk="MEDIUM",
            action="WAIT",
            validation_status="REJECTED"
        )
    )


    analyzer = DecisionAnalyzer()


    result = analyzer.analyze_history(
        history
    )


    assert result["total_decisions"] == 2
    assert result["approved"] == 1
    assert result["rejected"] == 1
    assert result["average_confidence"] == 70