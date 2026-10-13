from analysis.confidence_engine import ConfidenceEngine


def test_confidence_engine():

    engine = ConfidenceEngine()

    signals = [
        "Bullish Trend",
        "Positive Momentum",
        "Overbought"
    ]

    result = engine.calculate(signals)

    print("Confidence Score:", result["confidence"])
    print("Factors:", result["factors"])

    assert result["confidence"] == 70

    assert result["factors"]["Bullish Trend"] == 15
    assert result["factors"]["Positive Momentum"] == 15
    assert result["factors"]["Overbought"] == -10
def test_confidence_engine_oversold_factor():
    engine = ConfidenceEngine()

    result = engine.calculate(["Oversold"])

    assert result["factors"]["Oversold"] == 10
    assert result["confidence"] == 60
