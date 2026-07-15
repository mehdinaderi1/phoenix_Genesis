from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow
from intelligence.generator import ReportGenerator


def test_reasoning_report_flow():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()

    report = flow.create_report(consensus)

    generator = ReportGenerator()

    output = generator.generate(report)

    assert report.symbol == "BTCUSDT"
    assert report.signal == "BUY"
    assert report.risk == "LOW"
    assert "High confidence score" in report.reasons

    assert "PHOENIX MARKET REPORT" in output
    assert "BUY" in output