from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight
)


def test_low_success_rate():

    engine = StrategyEvolutionInsight()

    insight = engine.analyze(

        {},

        {},

        {

            "score": 85,

            "success_rate": 0.40

        }

    )

    assert insight.learning is True

    assert insight.reason == "Low success rate"


def test_low_score():

    engine = StrategyEvolutionInsight()

    insight = engine.analyze(

        {},

        {},

        {

            "score": 45,

            "success_rate": 0.80

        }

    )

    assert insight.learning is True

    assert insight.reason == "Low strategy score"


def test_keep_learning_false():

    engine = StrategyEvolutionInsight()

    insight = engine.analyze(

        {},

        {},

        {

            "score": 90,

            "success_rate": 0.90

        }

    )

    assert insight.learning is False

    assert insight.reason == "Stable strategy"