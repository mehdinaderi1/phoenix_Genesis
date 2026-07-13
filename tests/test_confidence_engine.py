from analysis.confidence_engine import ConfidenceEngine


def test():

    engine = ConfidenceEngine()

    signals = [
        "Bullish Trend",
        "Positive Momentum",
        "Overbought"
    ]

    score = engine.calculate(signals)

    print("Confidence Score:", score)

    assert score > 0

    print("✅ Confidence Engine Passed")


if __name__ == "__main__":
    test()