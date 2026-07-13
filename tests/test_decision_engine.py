from analysis.decision_engine import DecisionEngine


def test():

    engine = DecisionEngine()

    signals = [
        "Bullish Trend",
        "Positive Momentum",
        "Overbought"
    ]

    result = engine.decide(
        70,
        signals
    )

    print(result)

    assert result["decision"] == "WATCH"

    print("✅ Decision Engine Passed")


if __name__ == "__main__":
    test()