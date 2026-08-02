from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
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



def test_evolution_analytics_count():

    history = MockHistory(
        [
            MockRecord(
                "v1",
                "v2",
                70,
                80
            ),
            MockRecord(
                "v2",
                "v3",
                80,
                90
            )
        ]
    )


    analytics = EvolutionAnalytics(
        history
    )


    assert analytics.count() == 2



def test_evolution_analytics_best_child():

    history = MockHistory(
        [
            MockRecord(
                "v1",
                "v2",
                70,
                80
            ),
            MockRecord(
                "v2",
                "v3",
                80,
                95
            )
        ]
    )


    analytics = EvolutionAnalytics(
        history
    )


    best = analytics.best_child()


    assert best.child == "v3"

    assert best.score_after == 95



def test_average_improvement():

    history = MockHistory(
        [
            MockRecord(
                "v1",
                "v2",
                70,
                80
            ),
            MockRecord(
                "v2",
                "v3",
                80,
                90
            )
        ]
    )


    analytics = EvolutionAnalytics(
        history
    )


    assert (
        analytics.average_improvement()
        ==
        10
    )



def test_lineage_growth():

    history = MockHistory(
        [
            MockRecord(
                "v1",
                "v2",
                70,
                80
            ),
            MockRecord(
                "v1",
                "v3",
                70,
                90
            )
        ]
    )


    analytics = EvolutionAnalytics(
        history
    )


    assert (
        analytics.lineage_growth("v1")
        ==
        15
    )



def test_empty_history():

    history = MockHistory([])


    analytics = EvolutionAnalytics(
        history
    )


    assert analytics.count() == 0

    assert analytics.best_child() is None

    assert analytics.average_improvement() == 0

    assert analytics.lineage_growth("unknown") == 0