from intelligence.performance_analyzer import PerformanceAnalyzer
from intelligence.decision_record import DecisionRecord


def test_performance_analyzer_v2():

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
            regime="TRENDING",
            signal="SELL",
            confidence=75,
            risk="LOW",
            action="PREPARE_SHORT",
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


    analyzer = PerformanceAnalyzer()

    result = analyzer.analyze(records)


    assert result["total_decisions"] == 3

    assert result["approval_rate"] == 66.66666666666666

    assert result["by_regime"]["TRENDING"]["total"] == 2

    assert result["by_regime"]["TRENDING"]["approved"] == 2

    assert result["by_action"]["PREPARE_LONG"]["total"] == 1