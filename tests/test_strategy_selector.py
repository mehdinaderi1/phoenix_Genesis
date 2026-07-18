from intelligence.strategy_selector import StrategySelector


class MockStrategyRecall:

    def recall(
        self,
        regime,
        signal,
        risk
    ):

        return [
            {
                "strategy": "trend_following",
                "score": 80
            },
            {
                "strategy": "mean_reversion",
                "score": 60
            }
        ]



class MockStrategyRanking:

    def rank(
        self,
        strategies
    ):

        return sorted(
            strategies,
            key=lambda x: x["score"],
            reverse=True
        )



def test_strategy_selector_returns_best_strategy():

    selector = StrategySelector(
        strategy_recall=MockStrategyRecall(),
        strategy_ranking=MockStrategyRanking()
    )


    result = selector.select(
        "bullish",
        "LONG",
        "medium"
    )


    assert result["strategy"] == "trend_following"

    assert result["score"] == 80



def test_strategy_selector_returns_none_when_no_strategy():


    class EmptyRecall:

        def recall(
            self,
            regime,
            signal,
            risk
        ):
            return []



    selector = StrategySelector(
        strategy_recall=EmptyRecall(),
        strategy_ranking=MockStrategyRanking()
    )


    result = selector.select(
        "unknown",
        "WAIT",
        "high"
    )


    assert result is None