from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_strategy_evaluates_real_mtf_breakdown_shape():
    strategy = BTCMTFTrendAlignmentV1()

    breakdown = {
        "timeframes": [
            {"timeframe": "5m", "confidence": 70, "weight": 1, "signal": "BUY", "trend": "BULLISH"},
            {"timeframe": "15m", "confidence": 70, "weight": 1, "signal": "BUY", "trend": "BULLISH"},
            {"timeframe": "30m", "confidence": 70, "weight": 1, "signal": "BUY", "trend": "BULLISH"},
            {"timeframe": "4H", "confidence": 70, "weight": 2, "signal": "BUY", "trend": "BULLISH"},
            {"timeframe": "1D", "confidence": 70, "weight": 3, "signal": "BUY", "trend": "BULLISH"},
        ]
    }

    timeframe_states = strategy.states_from_breakdown(breakdown)

    assert timeframe_states == {
        "5m": "BUY",
        "15m": "BULLISH",
        "30m": "BULLISH",
        "4H": "BULLISH",
        "1D": "BULLISH",
    }

    result = strategy.evaluate(timeframe_states)

    assert result["signal"] == "BUY"
    assert result["direction"] == "LONG"
    assert result["matched"] is True
