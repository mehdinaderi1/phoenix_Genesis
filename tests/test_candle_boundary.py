import pytest

from core.market_data.candle_boundary import get_candle_boundary


@pytest.mark.parametrize("timeframe, duration", [
    ("5m", 300),
    ("15m", 900),
    ("30m", 1800),
    ("4H", 14400),
    ("1D", 86400),
])
def test_candle_boundary_uses_timeframe_duration(timeframe, duration):
    boundary = get_candle_boundary(1001, timeframe)

    assert boundary.candle_start == (1001 // duration) * duration
    assert boundary.next_boundary == boundary.candle_start + duration
    assert boundary.duration_seconds == duration


def test_candle_boundary_age_and_closed():
    boundary = get_candle_boundary(650, "5m")

    assert boundary.candle_start == 600
    assert boundary.next_boundary == 900
    assert boundary.age_seconds(700) == 100
    assert boundary.is_closed(899) is False
    assert boundary.is_closed(900) is True


def test_candle_boundary_does_not_allow_negative_age():
    boundary = get_candle_boundary(650, "5m")

    assert boundary.age_seconds(500) == 0
