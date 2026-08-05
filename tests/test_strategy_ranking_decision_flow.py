from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.strategy_bridge import StrategyBridge
from intelligence.decision_engine import DecisionEngine


def test_strategy_ranking_to_decision_flow():


    memory = StrategyMemory()


    memory.store(
        {
            "name": "trend_following",
            "strategy": "trend_following",
            "regime": "bullish",
            "signal": "BUY",
            "risk": "LOW",
            "score": 90,
            "success_rate": 0.85,
            "status": "ACTIVE"
        }
    )


    memory.store(
        {
            "name": "old_strategy",
            "strategy": "old_strategy",
            "regime": "bullish",
            "signal": "BUY",
            "risk": "LOW",
            "score": 95,
            "success_rate": 0.90,
            "status": "RETIRED"
        }
    )


    recall = StrategyRecall(
        memory
    )


    ranker = StrategyRanker()


    selector = StrategySelector(
        recall,
        ranker
    )


    selected = selector.select(
        "bullish",
        "BUY",
        "LOW"
    )


    assert selected is not None


    adapter = StrategyAdapter()


    strategy_version = adapter.convert(
        selected
    )


    assert strategy_version.status == "ACTIVE"


    bridge = StrategyBridge()


    champion = bridge.get_best_strategy(
        [
            strategy_version
        ]
    )


    assert champion is not None

    assert champion["status"] == "ACTIVE"


    class Report:

        signal = "BUY"

        risk = "LOW"

        confidence = 90

        champion_strategy = champion


    decision = DecisionEngine().decide(
        Report()
    )


    assert decision.action == "PREPARE_LONG"
    