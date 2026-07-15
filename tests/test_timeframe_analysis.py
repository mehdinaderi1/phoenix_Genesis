from analysis.timeframe import TimeframeAnalysis


def test_timeframe_analysis_creation():

    analysis = TimeframeAnalysis(
        timeframe="4H",
        trend="BULLISH",
        signal="BUY",
        confidence=80
    )

    result = analysis.summary()

    assert result["timeframe"] == "4H"
    assert result["trend"] == "BULLISH"
    assert result["signal"] == "BUY"
    assert result["confidence"] == 80