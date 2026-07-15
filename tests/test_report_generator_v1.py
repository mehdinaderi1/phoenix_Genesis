from intelligence.report import MarketReport
from intelligence.generator import ReportGenerator


def test_report_generator():

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="4H",
        trend="BULLISH",
        regime="TRENDING_BULLISH",
        signal="BUY",
        confidence=78,
        risk="MEDIUM",
        reasons=[
            "Price above MA",
            "MACD positive"
        ]
    )

    generator = ReportGenerator()

    output = generator.generate(report)

    assert "PHOENIX MARKET REPORT" in output
    assert "BTCUSDT" in output
    assert "BUY" in output
    assert "78%" in output
    assert "MACD positive" in output