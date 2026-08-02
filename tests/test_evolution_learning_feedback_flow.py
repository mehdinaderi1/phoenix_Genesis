from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)

from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight
)


class MockRecord:

    def __init__(
        self,
        parent,
        child,
        score_before,
        score_after
    ):
        self.parent = parent
        self.child = child
        self.score_before = score_before
        self.score_after = score_after


class MockHistory:

    def __init__(self, records):

        self.records = records


    def all(self):

        return self.records


    def children_of(self, parent):

        return [
            r
            for r in self.records
            if r.parent == parent
        ]



def test_evolution_learning_feedback_flow():

    history = MockHistory(

        [

            MockRecord(
                "strategy_v1",
                "strategy_v2",
                70,
                90
            )

        ]

    )


    analytics = EvolutionAnalytics(
        history
    )


    insight_engine = StrategyEvolutionInsight()


    improvement = (
        analytics.average_improvement()
    )


    assert improvement == 20


    record = history.all()[0]


    insight = insight_engine.analyze(

        old_strategy=record.parent,

        new_strategy=record.child,

        performance={

            "score": record.score_after,

            "success_rate": 0.9

        }

    )


    assert insight.learning is False


    assert (
        insight.reason
        ==
        "Stable strategy"
    )


    assert (
        insight.confidence
        ==
        0.95
    )



def test_learning_feedback_detects_weak_evolution():

    history = MockHistory(

        [

            MockRecord(
                "strategy_v1",
                "strategy_v2",
                80,
                50
            )

        ]

    )


    analytics = EvolutionAnalytics(
        history
    )


    insight_engine = StrategyEvolutionInsight()


    assert (
        analytics.average_improvement()
        ==
        -30
    )


    record = history.all()[0]


    insight = insight_engine.analyze(

        record.parent,

        record.child,

        {

            "score": record.score_after,

            "success_rate": 0.3

        }

    )


    assert (
        insight.reason
        ==
        "Low success rate"
    )


    assert insight.learning is True


    assert (
        insight.confidence
        ==
        0.90
    )