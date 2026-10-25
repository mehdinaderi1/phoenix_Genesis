from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_strategy_long_alignment():
    strategy = BTCMTFTrendAlignmentV1()

    result = strategy.evaluate({
        "4H": "BULLISH",
        "30m": "BULLISH",
        "15m": "BULLISH",
        "5m": "BUY",
    })

    assert result["signal"] == "BUY"
    assert result["direction"] == "LONG"
    assert result["matched"] is True


def test_btc_strategy_short_alignment():
    strategy = BTCMTFTrendAlignmentV1()

    result = strategy.evaluate({
        "4H": "BEARISH",
        "30m": "BEARISH",
        "15m": "BEARISH",
        "5m": "SELL",
    })

    assert result["signal"] == "SELL"
    assert result["direction"] == "SHORT"
    assert result["matched"] is True


def test_btc_strategy_conflict_preserves_primary_signal_without_matching():
    strategy = BTCMTFTrendAlignmentV1()

    result = strategy.evaluate({
        "4H": "BULLISH",
        "30m": "BEARISH",
        "15m": "BULLISH",
        "5m": "BUY",
    })

    assert result["signal"] == "BUY"
    assert result["direction"] == "LONG"
    assert result["matched"] is False
