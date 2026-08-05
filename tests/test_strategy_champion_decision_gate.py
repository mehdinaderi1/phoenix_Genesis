from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.decision_rules import DecisionRules


class MockReport:

    signal = "BUY"
    risk = "LOW"
    confidence = 90

    champion_strategy = None



def test_strategy_champion_decision_gate_allows_active_strategy():

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


    adapter = StrategyAdapter()


    champion = adapter.convert(
        selected
    )


    report = MockReport()


    report.champion_strategy = champion.to_dict()


    rules = DecisionRules()


    assert rules.strategy_is_valid(
        report
    ) is True



def test_strategy_champion_decision_gate_blocks_retired_strategy():

    memory = StrategyMemory()


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


    adapter = StrategyAdapter()


    champion = adapter.convert(
        selected
    )


    report = MockReport()


    report.champion_strategy = champion.to_dict()


    rules = DecisionRules()


    assert rules.strategy_is_valid(
        report
    ) is False