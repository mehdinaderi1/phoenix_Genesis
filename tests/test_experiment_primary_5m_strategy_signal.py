from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_primary_5m_sell_is_preserved_when_15m_is_not_bearish():
    strategy = BTCMTFTrendAlignmentV1()

    result = strategy.evaluate({
        "4H": "BEARISH",
        "30m": "BEARISH",
        "15m": "BULLISH",
        "5m": "SELL",
    })

    assert result["signal"] == "SELL"
