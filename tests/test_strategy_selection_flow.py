from intelligence.strategy_selector import StrategySelector
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_recall import StrategyRecall


class MockStrategyMemory:


    def find_by_pattern(
        self,
        regime,
        signal,
        risk
    ):

        return [
            {
                "strategy": "mean_reversion",
                "score": 60
            },
            {
                "strategy": "trend_following",
                "score": 90
            }
        ]



def test_strategy_selection_flow_returns_best_strategy():

    memory = MockStrategyMemory()


    recall = StrategyRecall(
        memory
    )


    ranker = StrategyRanker()


    selector = StrategySelector(
        recall,
        ranker
    )


    result = selector.select(
        "bullish",
        "LONG",
        "medium"
    )


    assert result["strategy"] == "trend_following"

    assert result["score"] == 90



def test_strategy_selection_flow_returns_none_without_match():


    class EmptyMemory:


        def find_by_pattern(
            self,
            regime,
            signal,
            risk
        ):

            return []



    recall = StrategyRecall(
        EmptyMemory()
    )


    selector = StrategySelector(
        recall,
        StrategyRanker()
    )


    result = selector.select(
        "unknown",
        "WAIT",
        "high"
    )


    assert result is None