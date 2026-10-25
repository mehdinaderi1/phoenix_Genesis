from analysis.timeframe import TimeframeAnalysis
from experiments.signal_matrix.market_data_probe import MarketDataMatrixProbe


class FakeReader:
    def get_close_prices(self, symbol, timeframe):
        if timeframe == "15m":
            return []
        if timeframe == "30m":
            raise RuntimeError("sample database failure")
        return [100.0, 101.0, 102.0]


class FakeAnalyzer:
    def analyze(self, prices, timeframe):
        return TimeframeAnalysis(
            timeframe=timeframe,
            trend="BULLISH",
            signal="BUY",
            confidence=78,
            reasons=("Bullish Trend", "Positive Momentum"),
        )


def test_probe_preserves_independent_timeframe_results():
    matrix = MarketDataMatrixProbe(
        FakeReader(), FakeAnalyzer()
    ).run(timeframes=("5m", "1D"))

    assert [item.state for item in matrix.all_signals()] == ["BUY", "BUY"]
    assert [item.timeframe for item in matrix.all_signals()] == ["5m", "1D"]


def test_probe_records_missing_data_instead_of_dropping_timeframe():
    matrix = MarketDataMatrixProbe(
        FakeReader(), FakeAnalyzer()
    ).run(timeframes=("15m",))

    result = matrix.all_signals()[0]
    assert result.state == "DATA_ERROR"
    assert result.data_valid is False
    assert "No close-price data" in result.reasons[0]


def test_probe_records_reader_exception():
    matrix = MarketDataMatrixProbe(
        FakeReader(), FakeAnalyzer()
    ).run(timeframes=("30m",))

    result = matrix.all_signals()[0]
    assert result.state == "DATA_ERROR"
    assert "sample database failure" in result.reasons[0]


def test_probe_maps_wait_to_no_signal():
    class WaitAnalyzer:
        def analyze(self, prices, timeframe):
            return TimeframeAnalysis(
                timeframe=timeframe,
                trend="NEUTRAL",
                signal="WAIT",
                confidence=50,
                reasons=("Mixed momentum",),
            )

    matrix = MarketDataMatrixProbe(
        FakeReader(), WaitAnalyzer()
    ).run(timeframes=("5m",))

    result = matrix.all_signals()[0]
    assert result.state == "NO_SIGNAL"
    assert result.reasons == ("Mixed momentum",)
