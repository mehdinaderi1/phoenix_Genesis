from intelligence.learning.experience_engine import (
    ExperienceEngine,
)


def test_create_success_experience():

    experience = ExperienceEngine().create_experience(
        symbol="BTCUSDT",
        strategy="Trend",
        regime="Bull",
        signal="MACD_CROSS",
        confidence=80,
        profit_loss=3.5,
    )

    assert experience.outcome == "SUCCESS"
    assert experience.profit_loss == 3.5