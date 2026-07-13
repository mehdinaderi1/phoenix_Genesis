from analysis.market_pipeline import MarketPipeline


def test():

    pipeline = MarketPipeline()

    report = pipeline.run(
        "BTCUSDT"
    )

    print(report)

    assert report["asset"] == "BTCUSDT"

    print("✅ Market Pipeline Passed")


if __name__ == "__main__":
    test()