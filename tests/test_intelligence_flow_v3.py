from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow


def test_intelligence_flow_v3():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()

    report = flow.create_report(
        consensus
    )

    assert report.symbol == "BTCUSDT"

    assert report.trend == "BULLISH"

    assert report.signal == "BUY"

    assert report.confidence == 85

    assert report.risk == "LOW"

    assert "High confidence consensus" in report.reasons

    assert "Bullish trend confirmed" in report.reasons