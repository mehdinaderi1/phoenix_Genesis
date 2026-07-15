from intelligence.report import MarketReport


def test_market_report_creation():

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="4H",
        trend="BULLISH",
        signal="BUY",
        confidence=78,
        risk="MEDIUM",
        reasons=[
            "Price above MA",
            "MACD positive"
        ]
    )

    result = report.summary()

    assert result["symbol"] == "BTCUSDT"
    assert result["timeframe"] == "4H"
    assert result["trend"] == "BULLISH"
    assert result["signal"] == "BUY"
    assert result["confidence"] == 78
    assert result["risk"] == "MEDIUM"
    assert len(result["reasons"]) == 2