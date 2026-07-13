from analysis.phoenix_analyzer import PhoenixAnalyzer


def test():

    analyzer = PhoenixAnalyzer()

    report = analyzer.run(
        "BTCUSDT"
    )

    print(report)

    assert report["asset"] == "BTCUSDT"

    print("✅ Phoenix Analyzer Passed")


if __name__ == "__main__":
    test()