from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow
from intelligence.generator import ReportGenerator


def test_phoenix_report_flow():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()

    report = flow.create_report(
        consensus
    )

    generator = ReportGenerator()

    output = generator.generate(
        report
    )

    assert "PHOENIX MARKET REPORT" in output
    assert "BTCUSDT" in output
    assert "BUY" in output
    assert "85%" in output