from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector


def test_strategy_selector_preserves_ranked_champion_identity():

    memory = StrategyMemory()

    strategy_a = {
        "strategy": "strategy_A",
        "regime": "TREND",
        "signal": "BUY",
        "action": "BUY",
        "risk": "LOW",
        "samples": 20,
        "success_rate": 80,
        "score": 90,
        "status": "ACTIVE"
    }

    strategy_b = {
        "strategy": "strategy_B",
        "regime": "TREND",
        "signal": "BUY",
        "action": "BUY",
        "risk": "LOW",
        "samples": 20,
        "success_rate": 70,
        "score": 70,
        "status": "ACTIVE"
    }

    memory.store(strategy_a)
    memory.store(strategy_b)

    recall = StrategyRecall(
        memory
    )

    ranking = StrategyRanker()

    selector = StrategySelector(
        strategy_recall=recall,
        strategy_ranking=ranking
    )

    result = selector.select_with_result(
        "TREND",
        "BUY",
        "LOW"
    )

    assert result is not None

    champion = result["champion"]

    assert champion["strategy"] == "strategy_A"

    assert champion is (
        result["ranking"]
        .top_strategy
        .strategy_record
    )

    assert (
        result["ranking"]
        .top_strategy
        .strategy_name
        == "strategy_A"
    )

    assert [
        item.strategy_name
        for item in result["ranking"].ranked_strategies
    ] == [
        "strategy_A",
        "strategy_B"
    ]
