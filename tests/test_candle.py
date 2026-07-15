from market.candle import Candle


def test_candle_creation():

    candle = Candle(
        symbol="BTCUSDT",
        timeframe="4H",
        timestamp=1752451200,
        open=65000,
        high=66000,
        low=64500,
        close=65500,
        volume=1200
    )

    data = candle.to_dict()

    assert data["symbol"] == "BTCUSDT"
    assert data["timeframe"] == "4H"
    assert data["close"] == 65500
    assert data["volume"] == 1200


    print("✅ Candle Model Test Passed")


if __name__ == "__main__":
    test_candle_creation()