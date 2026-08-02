from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight
)


class AdaptiveEvolutionDecision:

    def decide(self, insight, score_before, score_after):

        if insight.learning:

            if score_after < score_before:

                return "IMPROVE"

            return "KEEP_LEARNING"


        if score_after > score_before:

            return "ACCEPT"


        return "REVIEW"



def test_adaptive_decision_accepts_successful_evolution():

    insight_engine = StrategyEvolutionInsight()

    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 90,
            "success_rate": 0.95
        }

    )


    decision_engine = AdaptiveEvolutionDecision()


    decision = decision_engine.decide(

        insight,

        70,

        90

    )


    assert decision == "ACCEPT"



def test_adaptive_decision_requests_improvement():

    insight_engine = StrategyEvolutionInsight()

    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 40,
            "success_rate": 0.3
        }

    )


    decision_engine = AdaptiveEvolutionDecision()


    decision = decision_engine.decide(

        insight,

        80,

        40

    )


    assert decision == "IMPROVE"



def test_adaptive_decision_keeps_learning_signal():

    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 55,
            "success_rate": 0.45
        }

    )


    decision_engine = AdaptiveEvolutionDecision()


    decision = decision_engine.decide(

        insight,

        50,

        55

    )


    assert decision == "KEEP_LEARNING"



def test_adaptive_decision_reviews_neutral_case():

    insight_engine = StrategyEvolutionInsight()


    insight = insight_engine.analyze(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 70,
            "success_rate": 0.7
        }

    )


    decision_engine = AdaptiveEvolutionDecision()


    decision = decision_engine.decide(

        insight,

        70,

        70

    )


    assert decision == "REVIEW"