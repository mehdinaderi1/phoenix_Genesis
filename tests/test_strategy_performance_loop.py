from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)


def test_strategy_performance_analyzer_reads_feedback():

    history = [

        {
            "result": "SUCCESS",
            "score": 100
        },

        {
            "result": "SUCCESS",
            "score": 100
        },

        {
            "result": "FAILED",
            "score": 0
        }

    ]


    analyzer = StrategyPerformanceAnalyzer()


    result = analyzer.analyze(
        history
    )


    assert result["samples"] == 3

    assert result["success_rate"] == 2 / 3