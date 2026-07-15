from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


def test_multitimeframe_analyzer_bullish():

    analyses = [
        TimeframeAnalysis(
            timeframe="30m",
            trend="BULLISH",
            signal="BUY",
            confidence=70
        ),
        TimeframeAnalysis(
            timeframe="4H",
            trend="BULLISH",
            signal="BUY",
            confidence=85
        ),
        TimeframeAnalysis(
            timeframe="Daily",
            trend="BULLISH",
            signal="BUY",
            confidence=90
        )
    ]

    analyzer = MultiTimeframeAnalyzer()

    result = analyzer.analyze(analyses)

    assert result.trend == "BULLISH"
    assert result.signal == "BUY"
    assert result.confidence == 81.66666666666667