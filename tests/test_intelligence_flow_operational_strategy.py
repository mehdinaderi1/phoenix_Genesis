from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow


def test_operational_strategy_result_is_exposed_in_report():
    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85,
        breakdown={
            "timeframes": [
                {"timeframe": "5m", "signal": "BUY", "trend": "BULLISH"},
                {"timeframe": "15m", "signal": "BUY", "trend": "BULLISH"},
                {"timeframe": "30m", "signal": "BUY", "trend": "BULLISH"},
                {"timeframe": "4H", "signal": "BUY", "trend": "BULLISH"}
            ]
        }
    )

    flow = IntelligenceFlow()
    report = flow.create_report(consensus)

    assert report.operational_strategy_result == {
        "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
        "signal": "BUY",
        "direction": "LONG",
        "matched": True,
    }


def test_operational_strategy_short_result_is_exposed_in_report():
    consensus = ConsensusResult(
        trend="BEARISH",
        signal="SELL",
        confidence=85,
        breakdown={
            "timeframes": [
                {"timeframe": "5m", "signal": "SELL", "trend": "BEARISH"},
                {"timeframe": "15m", "signal": "SELL", "trend": "BEARISH"},
                {"timeframe": "30m", "signal": "SELL", "trend": "BEARISH"},
                {"timeframe": "4H", "signal": "SELL", "trend": "BEARISH"}
            ]
        }
    )

    flow = IntelligenceFlow()
    report = flow.create_report(consensus)

    assert report.operational_strategy_result == {
        "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
        "signal": "SELL",
        "direction": "SHORT",
        "matched": True,
    }


def test_operational_strategy_conflict_returns_wait_in_report():
    consensus = ConsensusResult(
        trend="MIXED",
        signal="WAIT",
        confidence=50,
        breakdown={
            "timeframes": [
                {"timeframe": "5m", "signal": "BUY", "trend": "BULLISH"},
                {"timeframe": "15m", "signal": "BUY", "trend": "BULLISH"},
                {"timeframe": "30m", "signal": "SELL", "trend": "BEARISH"},
                {"timeframe": "4H", "signal": "BUY", "trend": "BULLISH"}
            ]
        }
    )

    flow = IntelligenceFlow()
    report = flow.create_report(consensus)

    assert report.operational_strategy_result == {
        "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
        "signal": "WAIT",
        "direction": None,
        "matched": False,
    }
