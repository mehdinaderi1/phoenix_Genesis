from reasoning.engine import ReasoningEngine
from intelligence.report_builder import ReportBuilder


def test_intelligence_pipeline():

    # Simulated analysis output
    analysis_data = {
        "trend": "Bullish",
        "momentum": "Positive",
        "regime": "Trending"
    }

    # Reasoning layer
    reasoning_engine = ReasoningEngine()

    reasoning_output = reasoning_engine.analyze(
        analysis_data
    )

    # Report generation
    builder = ReportBuilder()

    report = builder.build(
        symbol="BTCUSDT",
        reasoning_output=reasoning_output,
        risk_level="Medium",
        confidence=78
    )

    result = report.summary()

    assert result["symbol"] == "BTCUSDT"
    assert result["trend"] == "Bullish"
    assert result["momentum"] == "Positive"
    assert result["risk_level"] == "Medium"
    assert result["confidence"] == 78

    assert "bullish" in result["reasoning"].lower()