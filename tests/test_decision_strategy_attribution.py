from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.decision_record import DecisionRecord



def test_decision_record_keeps_champion_strategy():

    memory = StrategyMemory()

    memory.store(
        {
            "strategy": "TREND_BUY_LOW",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 20,
            "success_rate": 0.85,
            "score": 90,
            "status": "ACTIVE"
        }
    )


    recall = StrategyRecall(memory)

    ranker = StrategyRanker()

    selector = StrategySelector(
        recall,
        ranker
    )


    result = selector.select_with_result(
        "TREND",
        "BUY",
        "LOW"
    )


    champion = result["champion"]


    record = DecisionRecord(
        symbol="BTCUSDT",
        timeframe="30m",
        regime="TREND",
        signal="BUY",
        confidence=85,
        risk="LOW",
        action="PREPARE_LONG",
        validation_status="APPROVED",
        champion_strategy=champion
    )


    assert record.champion_strategy is not None

    assert (
        record.champion_strategy["strategy"]
        == "TREND_BUY_LOW"
    )