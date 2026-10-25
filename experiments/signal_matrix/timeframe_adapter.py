from experiments.signal_matrix.signal_matrix import (
    SignalMatrix,
    StrategySignal,
)


def _diagnose_wait(analysis, reasons):
    """Classify WAIT without changing the original analysis."""

    trend = getattr(analysis, "trend", None)

    has_bullish_trend = "Bullish Trend" in reasons
    has_bearish_trend = "Bearish Trend" in reasons
    has_positive_momentum = "Positive Momentum" in reasons
    has_negative_momentum = "Negative Momentum" in reasons

    if (
        (has_bullish_trend and has_negative_momentum)
        or (has_bearish_trend and has_positive_momentum)
    ):
        return "TREND_MOMENTUM_CONFLICT"

    if trend == "NEUTRAL" or (
        not has_bullish_trend and not has_bearish_trend
    ):
        return "TREND_NOT_CONFIRMED"

    if (
        (has_bullish_trend and not has_positive_momentum)
        or (has_bearish_trend and not has_negative_momentum)
    ):
        return "MOMENTUM_CONFIRMATION_MISSING"

    return "INSUFFICIENT_SIGNAL"


def record_timeframe_analysis(
    matrix: SignalMatrix,
    strategy: str,
    analysis,
    timestamp: str | None = None,
) -> StrategySignal:
    """Record an analysis without modifying its signal or original reasons."""

    raw_signal = getattr(analysis, "signal", None)

    if raw_signal in ("BUY", "SELL"):
        state = raw_signal
    elif raw_signal == "WAIT":
        state = "NO_SIGNAL"
    else:
        state = "NOT_EVALUATED"

    raw_confidence = getattr(analysis, "confidence", None)
    confidence = (
        float(raw_confidence)
        if raw_confidence is not None
        else None
    )

    raw_reasons = getattr(analysis, "reasons", ())
    reasons = (
        (raw_reasons,)
        if isinstance(raw_reasons, str)
        else tuple(raw_reasons or ())
    )

    diagnostic_code = (
        _diagnose_wait(analysis, reasons)
        if raw_signal == "WAIT"
        else None
    )

    result = StrategySignal(
        strategy=strategy,
        timeframe=str(getattr(analysis, "timeframe", "") or ""),
        state=state,
        confidence=confidence,
        timestamp=timestamp,
        reasons=reasons,
        diagnostic_code=diagnostic_code,
    )
    matrix.add(result)
    return result
