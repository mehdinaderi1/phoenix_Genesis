from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


def test_multitimeframe_conflict():

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
            confidence=80
        ),
        TimeframeAnalysis(
            timeframe="Daily",
            trend="BEARISH",
            signal="SELL",
            confidence=90
        )
    ]

    analyzer = MultiTimeframeAnalyzer()

    result = analyzer.analyze(analyses)

    assert result.signal == "WAIT"
    assert result.confidence == 40