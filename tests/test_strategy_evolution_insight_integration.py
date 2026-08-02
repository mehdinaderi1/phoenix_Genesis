from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight,
    EvolutionInsight
)


def test_strategy_evolution_insight_detects_improvement_need():

    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        old_strategy="strategy_v1",

        new_strategy="strategy_v2",

        performance={
            "score": 70,
            "success_rate": 0.4
        }

    )


    assert isinstance(
        insight,
        EvolutionInsight
    )


    assert (
        insight.reason
        ==
        "Low success rate"
    )


    assert (
        insight.learning
        is True
    )


    assert (
        insight.confidence
        ==
        0.90
    )



def test_strategy_evolution_insight_handles_improve_decision():

    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 80,
            "success_rate": 0.8
        },

        decision="IMPROVE"

    )


    assert (
        insight.reason
        ==
        "Strategy needs improvement"
    )


    assert (
        insight.improvement
        ==
        "Optimize strategy parameters"
    )


    assert insight.learning is True



def test_strategy_evolution_insight_stable_strategy():

    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 90,
            "success_rate": 0.95
        }

    )


    assert (
        insight.reason
        ==
        "Stable strategy"
    )


    assert insight.learning is False

    assert insight.confidence == 0.95