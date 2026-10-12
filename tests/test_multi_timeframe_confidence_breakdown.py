from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


def test_multi_timeframe_analyzer_builds_confidence_breakdown():
    analyzer = MultiTimeframeAnalyzer()

    analyses = [
        TimeframeAnalysis("5m", "BEARISH", "WAIT", 50),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "WAIT", 40),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    result = analyzer.analyze(analyses)
    breakdown = result.breakdown

    assert breakdown is not None
    assert breakdown["weighted_confidence"] == 63.75
    assert breakdown["signal_conflict"] is True
    assert breakdown["conflict_penalty"] == 0.5
    assert breakdown["final_confidence"] == 31.875

    assert breakdown["timeframes"] == [
        {
            "timeframe": "5m",
            "confidence": 50,
            "weight": 1,
            "signal": "WAIT",
            "trend": "BEARISH",
            "reasons": [],
        },
        {
            "timeframe": "15m",
            "confidence": 70,
            "weight": 1,
            "signal": "BUY",
            "trend": "BULLISH",
            "reasons": [],
        },
        {
            "timeframe": "30m",
            "confidence": 40,
            "weight": 1,
            "signal": "WAIT",
            "trend": "BULLISH",
            "reasons": [],
        },
        {
            "timeframe": "4H",
            "confidence": 70,
            "weight": 2,
            "signal": "BUY",
            "trend": "BULLISH",
            "reasons": [],
        },
        {
            "timeframe": "1D",
            "confidence": 70,
            "weight": 3,
            "signal": "BUY",
            "trend": "BULLISH",
            "reasons": [],
        },
    ]


def test_multi_timeframe_analyzer_preserves_timeframe_reasons():
    analyzer = MultiTimeframeAnalyzer()

    analyses = [
        TimeframeAnalysis(
            "5m",
            "BULLISH",
            "WAIT",
            50,
            reasons=("Bullish Trend", "Negative Momentum"),
        )
    ]

    result = analyzer.analyze(analyses)

    assert result.breakdown["timeframes"][0]["reasons"] == [
        "Bullish Trend",
        "Negative Momentum",
    ]
