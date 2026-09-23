"""Timeframe duration utilities."""

TIMEFRAME_SECONDS = {
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "4H": 14400,
    "1D": 86400,
}


def timeframe_seconds(timeframe):
    try:
        return TIMEFRAME_SECONDS[timeframe]
    except KeyError as exc:
        raise ValueError(f"Unsupported timeframe: {timeframe}") from exc
