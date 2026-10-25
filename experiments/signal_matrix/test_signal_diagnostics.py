from analysis.timeframe import TimeframeAnalysis
from experiments.signal_matrix.signal_matrix import SignalMatrix
from experiments.signal_matrix.timeframe_adapter import (
    record_timeframe_analysis,
)


def test_wait_with_bearish_trend_and_positive_momentum_is_conflict():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="5m",
        trend="BEARISH",
        signal="WAIT",
        confidence=50,
        reasons=("Bearish Trend", "Positive Momentum"),
    )

    recorded = record_timeframe_analysis(matrix, "TimeframeAnalyzer", analysis)

    assert recorded.state == "NO_SIGNAL"
    assert recorded.diagnostic_code == "TREND_MOMENTUM_CONFLICT"
    assert recorded.reasons == ("Bearish Trend", "Positive Momentum")


def test_wait_with_bullish_trend_and_negative_momentum_is_conflict():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="15m",
        trend="BULLISH",
        signal="WAIT",
        confidence=50,
        reasons=("Bullish Trend", "Negative Momentum"),
    )

    recorded = record_timeframe_analysis(matrix, "TimeframeAnalyzer", analysis)

    assert recorded.diagnostic_code == "TREND_MOMENTUM_CONFLICT"


def test_wait_with_neutral_trend_is_not_confirmed():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="30m",
        trend="NEUTRAL",
        signal="WAIT",
        confidence=50,
        reasons=("Neutral RSI", "Neutral Momentum"),
    )

    recorded = record_timeframe_analysis(matrix, "TimeframeAnalyzer", analysis)

    assert recorded.state == "NO_SIGNAL"
    assert recorded.diagnostic_code == "TREND_NOT_CONFIRMED"


def test_buy_keeps_original_signal_and_has_no_wait_diagnostic():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="1D",
        trend="BULLISH",
        signal="BUY",
        confidence=80,
        reasons=("Bullish Trend", "Positive Momentum"),
    )

    recorded = record_timeframe_analysis(matrix, "TimeframeAnalyzer", analysis)

    assert recorded.state == "BUY"
    assert recorded.diagnostic_code is None


def test_diagnostic_code_is_in_serialized_record():
    matrix = SignalMatrix()
    analysis = TimeframeAnalysis(
        timeframe="4H",
        trend="BEARISH",
        signal="WAIT",
        confidence=50,
        reasons=("Bearish Trend", "Positive Momentum"),
    )

    record_timeframe_analysis(matrix, "TimeframeAnalyzer", analysis)
    record = matrix.to_records()[0]

    assert record["diagnostic_code"] == "TREND_MOMENTUM_CONFLICT"
    assert record["reasons"] == ("Bearish Trend", "Positive Momentum")
