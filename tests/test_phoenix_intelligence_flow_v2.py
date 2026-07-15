from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer
from intelligence.report import MarketReport


def test_phoenix_intelligence_flow_v2():

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

    consensus = analyzer.analyze(analyses)

    report = MarketReport(
    symbol="BTCUSDT",
    timeframe="Multi",
    trend=consensus.trend,
    signal=consensus.signal,
    confidence=consensus.confidence,
    risk="LOW",
    reasons=[
        "Multi timeframe agreement",
        "High confidence consensus"
    ]
)

    assert report.symbol == "BTCUSDT"
    assert report.signal == "BUY"
    assert report.confidence == 81.66666666666667