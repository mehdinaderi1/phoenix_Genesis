"""Candle boundary calculation utilities."""

from dataclasses import dataclass

from core.market_data.timeframe import timeframe_seconds


@dataclass(frozen=True)
class CandleBoundary:
    timeframe: str
    candle_start: int
    next_boundary: int

    @property
    def duration_seconds(self):
        return timeframe_seconds(self.timeframe)

    def age_seconds(self, now):
        return max(0, now - self.candle_start)

    def is_closed(self, now):
        return now >= self.next_boundary


def get_candle_boundary(timestamp, timeframe):
    duration = timeframe_seconds(timeframe)
    candle_start = (timestamp // duration) * duration
    return CandleBoundary(
        timeframe=timeframe,
        candle_start=candle_start,
        next_boundary=candle_start + duration,
    )
