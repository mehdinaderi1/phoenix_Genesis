from analysis.timeframe_analyzer import TimeframeAnalyzer


def test_timeframe_analyzer():

    prices = [
        64000,
        64200,
        64500,
        64800,
        65000,
        65200,
        65500,
        65800,
        66000,
        66300,
        66500,
        66800,
        67000,
        67200,
        67500,
        67800,
        68000,
        68300,
        68500,
        68800,
        69000,
        69300,
        69500,
        69800,
        70000,
        70200,
        70500,
        70800,
        71000,
        71200
    ]

    analyzer = TimeframeAnalyzer()

    result = analyzer.analyze(
        prices,
        "30m"
    )

    assert result.timeframe == "30m"
    assert result.trend == "BULLISH"
    assert result.signal == "BUY"
    assert result.confidence > 0