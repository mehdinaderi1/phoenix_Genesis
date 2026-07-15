from intelligence.consensus import ConsensusResult
from intelligence.regime_analyzer import RegimeAnalyzer


def test_bullish_regime_detection():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    analyzer = RegimeAnalyzer()

    result = analyzer.analyze(consensus)

    assert result.regime == "TRENDING_BULLISH"
    assert result.confidence == 85
    assert len(result.reasons) > 0