from analysis.timeframe import TimeframeAnalysis
from experiments.signal_matrix.signal_matrix import SignalMatrix
from experiments.signal_matrix.timeframe_adapter import (
    record_timeframe_analysis,
)


def test_adapter_records_buy_from_existing_analysis():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="5m",
        trend="BULLISH",
        signal="BUY",
        confidence=82,
        reasons=("Bullish Trend", "Positive Momentum"),
    )

    recorded = record_timeframe_analysis(
        matrix, "ScalpStrategy", analysis, "2026-10-13T12:00:00"
    )

    assert recorded.state == "BUY"
    assert recorded.timeframe == "5m"
    assert recorded.confidence == 82
    assert recorded.timestamp == "2026-10-13T12:00:00"
    assert len(matrix.all_signals()) == 1


def test_adapter_maps_wait_to_no_signal_without_losing_reasons():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="15m",
        trend="NEUTRAL",
        signal="WAIT",
        confidence=50,
        reasons=("Mixed Trend",),
    )

    recorded = record_timeframe_analysis(matrix, "TrendStrategy", analysis)

    assert recorded.state == "NO_SIGNAL"
    assert recorded.reasons == ("Mixed Trend",)


def test_adapter_does_not_merge_independent_timeframes():
    matrix = SignalMatrix()

    buy = TimeframeAnalysis(
        timeframe="5m",
        trend="BULLISH",
        signal="BUY",
        confidence=75,
        reasons=("Scalp setup",),
    )
    sell = TimeframeAnalysis(
        timeframe="1D",
        trend="BEARISH",
        signal="SELL",
        confidence=84,
        reasons=("Daily setup",),
    )

    record_timeframe_analysis(matrix, "ScalpStrategy", buy)
    record_timeframe_analysis(matrix, "DailyStrategy", sell)

    assert [item.state for item in matrix.all_signals()] == ["BUY", "SELL"]
    assert len(matrix.for_timeframe("5m")) == 1
    assert len(matrix.for_timeframe("1D")) == 1
