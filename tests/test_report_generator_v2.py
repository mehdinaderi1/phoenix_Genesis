from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow
from intelligence.generator import ReportGenerator


def test_report_generator_v2():

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

    print(output)

    assert "PHOENIX MARKET REPORT" in output
    assert "BTCUSDT" in output
    assert "BUY" in output
    assert "85%" in output

    assert "Decision:" in output
    assert "PREPARE_LONG" in output

    assert "Validation:" in output
    assert "APPROVED" in output