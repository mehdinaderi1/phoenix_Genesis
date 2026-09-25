from analysis.timeframe import TimeframeAnalysis
from intelligence.multitimeframe import MultiTimeframeAnalyzer
from intelligence.trading_strategy import BTCMTFTrendAlignmentV1


def test_btc_strategy_consumes_real_mtf_analyzer_output():

    analyses = [
        TimeframeAnalysis("5m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("15m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("30m", "BULLISH", "BUY", 70),
        TimeframeAnalysis("4H", "BULLISH", "BUY", 70),
        TimeframeAnalysis("1D", "BULLISH", "BUY", 70),
    ]

    consensus = MultiTimeframeAnalyzer().analyze(analyses)

    strategy = BTCMTFTrendAlignmentV1()

    timeframe_states = strategy.states_from_breakdown(
        consensus.breakdown
    )

    result = strategy.evaluate(timeframe_states)

    assert result["signal"] == "BUY"
    assert result["direction"] == "LONG"
    assert result["matched"] is True
