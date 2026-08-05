from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.decision_engine import DecisionEngine


class MockReport:

    def __init__(
        self,
        signal,
        risk,
        confidence,
        champion_strategy
    ):

        self.signal = signal
        self.risk = risk
        self.confidence = confidence
        self.champion_strategy = champion_strategy



def test_strategy_intelligence_flows_into_decision():

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


    assert selected["name"] == "trend_following"


    adapter = StrategyAdapter()


    strategy_version = adapter.convert(
        selected
    )


    assert strategy_version.status == "ACTIVE"


    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90,
        champion_strategy=selected
    )


    engine = DecisionEngine()


    decision = engine.decide(
        report
    )


    assert decision.action == "PREPARE_LONG"