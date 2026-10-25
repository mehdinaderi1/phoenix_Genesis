import pytest

from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer


@pytest.mark.parametrize("daily_signal", ["WAIT", "BUY"])
def test_primary_5m_sell_survives_daily_disagreement(daily_signal):
    analyses = [
        TimeframeAnalysis(
            timeframe="5m",
            trend="BEARISH",
            signal="SELL",
            confidence=75,
        ),
        TimeframeAnalysis(
            timeframe="15m",
            trend="BEARISH",
            signal="SELL",
            confidence=70,
        ),
        TimeframeAnalysis(
            timeframe="30m",
            trend="BEARISH",
            signal="SELL",
            confidence=70,
        ),
        TimeframeAnalysis(
            timeframe="4H",
            trend="BEARISH",
            signal="SELL",
            confidence=70,
        ),
        TimeframeAnalysis(
            timeframe="1D",
            trend="BEARISH" if daily_signal == "WAIT" else "BULLISH",
            signal=daily_signal,
            confidence=50,
        ),
    ]

    result = MultiTimeframeAnalyzer().analyze(analyses)

    assert result.signal == "SELL"

def test_primary_5m_confidence_uses_weighted_average_and_conflict_penalty():
    analyses = [
        TimeframeAnalysis("5m", "BEARISH", "SELL", 75),
        TimeframeAnalysis("15m", "BEARISH", "SELL", 70),
        TimeframeAnalysis("30m", "BEARISH", "SELL", 70),
        TimeframeAnalysis("4H", "BEARISH", "SELL", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 50),
    ]

    result = MultiTimeframeAnalyzer().analyze(analyses)

    assert result.signal == "SELL"
    assert result.breakdown["weighted_confidence"] == pytest.approx(63.125)
    assert result.breakdown["signal_conflict"] is True
    assert result.breakdown["conflict_penalty"] == pytest.approx(0.5)
    assert result.confidence == pytest.approx(31.5625)

