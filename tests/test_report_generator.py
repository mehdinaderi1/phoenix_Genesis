from analysis.report_generator import ReportGenerator


def test():

    generator = ReportGenerator()

    report = generator.generate(
        "BTCUSDT",
        [
            "Bullish Trend",
            "Positive Momentum",
            "Overbought"
        ],
        70,
        "WATCH",
        "Medium"
    )

    print(report)

    assert report["asset"] == "BTCUSDT"
    assert report["confidence"] == 70
    assert report["decision"] == "WATCH"

    print("✅ Report Generator Passed")


if __name__ == "__main__":
    test()