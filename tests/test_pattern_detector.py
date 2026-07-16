from intelligence.learning.pattern_detector import (
    PatternDetector,
)
from intelligence.learning.experience_record import (
    ExperienceRecord,
)


def test_pattern_detection():

    experiences = [
        ExperienceRecord(
            symbol="BTCUSDT",
            strategy="Trend",
            regime="Bull",
            signal="MACD",
            confidence=80,
            outcome="SUCCESS",
            profit_loss=2,
            lesson="good",
        ),
        ExperienceRecord(
            symbol="BTCUSDT",
            strategy="Trend",
            regime="Bull",
            signal="MACD",
            confidence=75,
            outcome="FAILURE",
            profit_loss=-1,
            lesson="bad",
        ),
    ]

    result = PatternDetector().analyze(
        experiences
    )

    assert result[("Trend", "Bull")]["trades"] == 2
    assert result[("Trend", "Bull")]["win_rate"] == 50