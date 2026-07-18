from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)



def test_strategy_performance_analysis():

    analyzer = StrategyPerformanceAnalyzer()


    history = [

        {
            "strategy": "PREPARE_LONG",
            "score": 90,
            "success": True
        },

        {
            "strategy": "PREPARE_LONG",
            "score": 70,
            "success": True
        },

        {
            "strategy": "PREPARE_LONG",
            "score": 40,
            "success": False
        }

    ]


    result = analyzer.analyze(
        history
    )


    assert result["samples"] == 3

    assert result["success_rate"] == 2 / 3

    assert result["average_score"] == 66.66666666666667