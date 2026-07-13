from analysis.risk_engine import RiskEngine


def test():

    engine = RiskEngine()

    signals = [
        "Bullish Trend",
        "Positive Momentum",
        "Overbought"
    ]

    result = engine.analyze(
        70,
        signals
    )

    print(result)

    assert result["risk"] == "Medium"

    assert "Market may be overheated" in result["warnings"]

    print("✅ Risk Engine Passed")


if __name__ == "__main__":
    test()