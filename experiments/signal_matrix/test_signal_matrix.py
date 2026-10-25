from experiments.signal_matrix.signal_matrix import (
    EntryAuthorization,
    SignalMatrix,
    StrategySignal,
)


def test_matrix_preserves_opposing_signals():
    matrix = SignalMatrix()
    matrix.add(StrategySignal("Scalp", "5m", "BUY", 75))
    matrix.add(StrategySignal("Trend", "1D", "SELL", 82))

    assert len(matrix.all_signals()) == 2
    assert matrix.for_timeframe("5m")[0].state == "BUY"
    assert matrix.for_strategy("Trend")[0].state == "SELL"


def test_matrix_distinguishes_missing_and_unevaluated_signals():
    matrix = SignalMatrix()
    matrix.add(StrategySignal("Scalp", "5m", "NO_SIGNAL"))
    matrix.add(StrategySignal("Trend", "1D", "NOT_EVALUATED"))

    assert matrix.all_signals()[0].state == "NO_SIGNAL"
    assert matrix.all_signals()[1].state == "NOT_EVALUATED"


def test_data_error_is_marked_invalid():
    signal = StrategySignal("Scalp", "5m", "DATA_ERROR")

    assert signal.data_valid is False


def test_entry_authorization_is_separate_from_signal():
    signal = StrategySignal("Scalp", "5m", "BUY", 85)
    authorization = EntryAuthorization(
        authorized=False,
        block_reasons=("Risk gate blocked entry",),
    )

    assert signal.state == "BUY"
    assert authorization.authorized is False
    assert authorization.block_reasons


def test_invalid_confidence_is_rejected():
    try:
        StrategySignal("Scalp", "5m", "BUY", 120)
    except ValueError:
        return

    raise AssertionError("Invalid confidence should be rejected")
