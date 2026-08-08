from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_ranker import StrategyRanker
from intelligence.strategy_council import StrategyCouncil
from intelligence.decision_engine import DecisionEngine
from intelligence.market_report import MarketReport


def test_strategy_ranking_council_decision_flow():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "TREND_BUY_LOW",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 50,
            "success_rate": 0.90,
            "score": 95,
            "status": "ACTIVE",
            "action": "BUY",
            "confidence": 90
        }
    )


    memory.store(
        {
            "strategy": "BREAKOUT_BUY",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 40,
            "success_rate": 0.80,
            "score": 85,
            "status": "ACTIVE",
            "action": "BUY",
            "confidence": 80
        }
    )


    memory.store(
        {
            "strategy": "MEAN_REVERSION",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 30,
            "success_rate": 0.60,
            "score": 70,
            "status": "ACTIVE",
            "action": "WAIT",
            "confidence": 60
        }
    )


    recall = StrategyRecall(
        memory
    )


    strategies = recall.recall(
        "TREND",
        "BUY",
        "LOW"
    )


    ranker = StrategyRanker()


    ranking_result = (
        ranker.rank_with_result(
            strategies,
            market_context={
                "regime": "TREND",
                "signal": "BUY",
                "risk": "LOW"
            }
        )
    )


    assert ranking_result is not None

    assert ranking_result.top_strategy is not None


    council = StrategyCouncil()


    consensus = council.evaluate(
        ranking_result
    )


    assert consensus is not None

    assert consensus.get(
        "decision"
    ) == "BUY"


    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="UP",
        regime="TREND",
        signal="BUY",
        confidence=90,
        risk="LOW",
        reasons=[
            "multi strategy consensus"
        ],
        strategy_consensus=consensus
    )


    decision = DecisionEngine().decide(
        report
    )


    assert decision.action == (
        "PREPARE_LONG"
    )

    assert decision.explanation is not None