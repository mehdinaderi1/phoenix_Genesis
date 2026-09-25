from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_mtf_trend_alignment_v1_definition():
    strategy = BTCMTFTrendAlignmentV1()

    assert strategy.name == "BTC_MTF_TREND_ALIGNMENT_V1"
    assert strategy.symbol == "BTCUSDT"
    assert strategy.market == "FUTURES"
    assert strategy.primary_timeframe == "5m"
    assert strategy.context_timeframes == ["15m", "30m"]
    assert strategy.higher_timeframe == "4H"

    assert strategy.long_conditions == {
        "4H": "BULLISH",
        "30m": "BULLISH",
        "15m": "BULLISH",
        "5m": "BUY",
    }

    assert strategy.short_conditions == {
        "4H": "BEARISH",
        "30m": "BEARISH",
        "15m": "BEARISH",
        "5m": "SELL",
    }
