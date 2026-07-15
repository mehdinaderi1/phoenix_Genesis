from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow


def test_regime_in_flow():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()

    report = flow.create_report(consensus)

    assert report.signal == "BUY"

    assert (
        "Market Regime: TRENDING_BULLISH"
        in report.reasons
    )