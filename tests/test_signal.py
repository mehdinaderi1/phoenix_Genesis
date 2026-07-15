from analysis.signal import Signal


def test_signal_creation():

    signal = Signal(
        symbol="BTCUSDT",
        action="BUY",
        confidence=80,
        reasons=[
            "Price above MA",
            "MACD positive"
        ]
    )

    result = signal.summary()

    assert result["symbol"] == "BTCUSDT"
    assert result["action"] == "BUY"
    assert result["confidence"] == 80
    assert len(result["reasons"]) == 2