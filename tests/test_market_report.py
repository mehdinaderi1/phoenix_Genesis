from intelligence.market_report import MarketReport


def test_market_report():

    report = MarketReport(
        symbol="BTCUSDT",
        trend="Bullish",
        momentum="Positive",
        regime="Trending",
        risk_level="Medium",
        confidence=75,
        reasoning="Price above moving averages"
    )

    result = report.summary()

    assert result["symbol"] == "BTCUSDT"
    assert result["confidence"] == 75