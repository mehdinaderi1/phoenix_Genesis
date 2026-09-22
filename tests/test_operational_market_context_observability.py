from core.market_data.operational_market_context import OperationalMarketContext


def test_operational_market_context_accepts_optional_consensus_breakdown():
    breakdown = {
        "weighted_confidence": 63.75,
        "signal_conflict": True,
        "conflict_penalty": 0.5,
        "final_confidence": 31.875
    }

    context = OperationalMarketContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="WAIT",
        confidence=31.875,
        timestamp="2026-09-22T00:00:00+00:00",
        consensus_breakdown=breakdown
    )

    assert context.consensus_breakdown == breakdown


def test_operational_market_context_breakdown_is_optional():
    context = OperationalMarketContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=70,
        timestamp="2026-09-22T00:00:00+00:00"
    )

    assert context.consensus_breakdown is None
