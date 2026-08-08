from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.decision_engine import DecisionEngine
from intelligence.market_report import MarketReport


def test_strategy_to_decision_intelligence_cycle():

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


    recall = StrategyRecall(
        memory
    )


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


    assert result is not None


    champion = result["champion"]


    assert champion["strategy"] == (
        "TREND_BUY_LOW"
    )


    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="UP",
        regime="TREND",
        signal="BUY",
        confidence=85,
        risk="LOW",
        reasons=[
            "strategy champion"
        ],
        strategy_consensus={
            "decision": "BUY",
            "supporting_strategies": 3,
            "opposing_strategies": 0,
            "confidence": 0.9,
            "top_strategy": champion["strategy"]
        }
    )


    decision = DecisionEngine().decide(
        report
    )


    assert decision.action == (
        "PREPARE_LONG"
    )

    assert decision.explanation is not None