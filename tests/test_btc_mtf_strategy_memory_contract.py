from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_strategy_can_create_memory_record():
    strategy = BTCMTFTrendAlignmentV1()

    record = strategy.to_memory_record()

    assert record["strategy"] == "BTC_MTF_TREND_ALIGNMENT_V1"
    assert record["regime"] is None
    assert record["signal"] is None
    assert record["risk"] is None
    assert record["status"] == "CANDIDATE"
    assert record["samples"] == 0
    assert record["success_rate"] == 0
    assert record["score"] == 0
