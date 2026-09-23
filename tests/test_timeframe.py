import pytest

from core.market_data.timeframe import timeframe_seconds


@pytest.mark.parametrize("timeframe, expected", [
    ("5m", 300),
    ("15m", 900),
    ("30m", 1800),
    ("4H", 14400),
    ("1D", 86400),
])
def test_timeframe_seconds(timeframe, expected):
    assert timeframe_seconds(timeframe) == expected


@pytest.mark.parametrize("timeframe", ["", "1h", "7m", "invalid"])
def test_timeframe_seconds_rejects_unsupported(timeframe):
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        timeframe_seconds(timeframe)
