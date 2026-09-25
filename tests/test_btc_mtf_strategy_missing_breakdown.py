from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_strategy_handles_missing_breakdown():
    strategy = BTCMTFTrendAlignmentV1()

    states = strategy.states_from_breakdown(None)

    assert states == {}
