from core.market_data.candle_boundary import get_candle_boundary


def test_candle_boundary_observability_for_5m():
    boundary = get_candle_boundary(1790111100, "5m")

    assert boundary.timeframe == "5m"
    assert boundary.candle_start == 1790111100
    assert boundary.next_boundary == 1790111400
    assert boundary.duration_seconds == 300

    assert boundary.age_seconds(1790111200) == 100
    assert boundary.is_closed(1790111200) is False
    assert boundary.is_closed(1790111400) is True
