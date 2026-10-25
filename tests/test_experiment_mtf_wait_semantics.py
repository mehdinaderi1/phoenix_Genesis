from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


def make_analysis(timeframe, signal, confidence):
    trend = {
        "BUY": "BULLISH",
        "SELL": "BEARISH",
        "WAIT": "NEUTRAL",
    }[signal]

    return TimeframeAnalysis(
        timeframe=timeframe,
        trend=trend,
        signal=signal,
        confidence=confidence,
    )


def test_sell_and_wait_currently_produce_wait():
    analyzer = MultiTimeframeAnalyzer()

    result = analyzer.analyze([
        make_analysis("30m", "SELL", 70),
        make_analysis("4H", "WAIT", 50),
    ])

    assert result.signal == "WAIT"
    assert result.breakdown["signal_conflict"] is True
    assert result.breakdown["conflict_penalty"] == 0.5


def test_sell_majority_with_wait_currently_produces_wait():
    analyzer = MultiTimeframeAnalyzer()

    result = analyzer.analyze([
        make_analysis("30m", "SELL", 70),
        make_analysis("4H", "SELL", 80),
        make_analysis("1D", "WAIT", 50),
    ])

    assert result.signal == "WAIT"
    assert result.breakdown["signal_conflict"] is True
    assert result.breakdown["conflict_penalty"] == 0.5


def test_buy_and_sell_currently_produce_wait():
    analyzer = MultiTimeframeAnalyzer()

    result = analyzer.analyze([
        make_analysis("30m", "BUY", 70),
        make_analysis("4H", "SELL", 80),
    ])

    assert result.signal == "WAIT"
    assert result.breakdown["signal_conflict"] is True
    assert result.breakdown["conflict_penalty"] == 0.5
