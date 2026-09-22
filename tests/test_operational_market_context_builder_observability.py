from core.market_data.operational_market_context_builder import OperationalMarketContextBuilder
from intelligence.consensus import ConsensusResult


def test_builder_propagates_consensus_breakdown():
    breakdown = {
        "timeframes": [
            {"timeframe": "5m", "confidence": 50, "weight": 1, "signal": "WAIT"},
            {"timeframe": "15m", "confidence": 70, "weight": 1, "signal": "BUY"},
        ],
        "weighted_confidence": 63.75,
        "signal_conflict": True,
        "conflict_penalty": 0.5,
        "final_confidence": 31.875
    }

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="WAIT",
        confidence=31.875,
        breakdown=breakdown
    )

    builder = OperationalMarketContextBuilder()
    context = builder.build("BTCUSDT", consensus)

    assert context.consensus_breakdown == breakdown
