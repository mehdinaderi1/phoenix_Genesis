from intelligence.report_builder import ReportBuilder


def test_report_builder():

    reasoning_output = {
        "trend": "Bullish",
        "momentum": "Positive",
        "regime": "Trending",
        "reasoning": "Market structure is showing bullish confirmation."
    }

    builder = ReportBuilder()

    report = builder.build(
        symbol="BTCUSDT",
        reasoning_output=reasoning_output,
        risk_level="Medium",
        confidence=75
    )

    result = report.summary()

    assert result["symbol"] == "BTCUSDT"
    assert result["trend"] == "Bullish"
    assert result["confidence"] == 75