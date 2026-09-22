from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


def test_consensus_confidence_breakdown_all_signals_match():
    analyzer = MultiTimeframeAnalyzer()
    analyses = [
        TimeframeAnalysis("5m", "BULLISH", "BUY", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    result = analyzer.analyze(analyses)

    assert result.signal == "BUY"
    assert result.confidence == 63.75


def test_consensus_confidence_breakdown_with_signal_conflict():
    analyzer = MultiTimeframeAnalyzer()
    analyses = [
        TimeframeAnalysis("5m", "BEARISH", "WAIT", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "WAIT", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    result = analyzer.analyze(analyses)

    assert result.signal == "WAIT"
    assert result.confidence == 31.875


def test_consensus_confidence_breakdown_lower_timeframe_conflict():
    analyzer = MultiTimeframeAnalyzer()
    matching = [
        TimeframeAnalysis("5m", "BULLISH", "BUY", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]
    conflicting = [
        TimeframeAnalysis("5m", "BEARISH", "SELL", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    matching_result = analyzer.analyze(matching)
    conflicting_result = analyzer.analyze(conflicting)

    assert matching_result.confidence == 63.75
    assert conflicting_result.confidence == 31.875
    assert conflicting_result.signal == "WAIT"


def test_consensus_confidence_breakdown_higher_timeframe_conflict():
    analyzer = MultiTimeframeAnalyzer()
    matching = [
        TimeframeAnalysis("5m", "BULLISH", "BUY", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]
    conflicting = [
        TimeframeAnalysis("5m", "BULLISH", "BUY", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 40),
        TimeframeAnalysis("4H", "BEARISH", "SELL", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    matching_result = analyzer.analyze(matching)
    conflicting_result = analyzer.analyze(conflicting)

    assert matching_result.confidence == 63.75
    assert conflicting_result.confidence == 31.875
    assert conflicting_result.signal == "WAIT"
