from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.consensus import ConsensusResult


def test_risk_analyzer():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    analyzer = RiskAnalyzer()

    result = analyzer.analyze(consensus)

    assert result.level == "LOW"
    assert result.score == 85