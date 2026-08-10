from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector
from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.strategy_bridge import StrategyBridge
from intelligence.decision_engine import DecisionEngine
from intelligence.strategy_council import StrategyCouncil
from intelligence.report import MarketReport


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

def test_strategy_consensus_conflict_with_market_signal_blocks_long():

    memory = StrategyMemory()

    memory.store(
        {
            "strategy": "TREND_SELL_LOW",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 50,
            "success_rate": 0.90,
            "score": 95,
            "status": "ACTIVE",
            "action": "SELL",
            "confidence": 90
        }
    )

    recall = StrategyRecall(memory)

    strategies = recall.recall(
        "TREND",
        "BUY",
        "LOW"
    )

    ranker = StrategyRanker()

    ranking_result = ranker.rank_with_result(
        strategies,
        market_context={
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW"
        }
    )

    consensus = StrategyCouncil().evaluate(
        ranking_result
    )

    assert consensus.get("decision") == "SELL"

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="UP",
        regime="TREND",
        signal="BUY",
        confidence=90,
        risk="LOW",
        reasons=[
            "strategy consensus conflicts with market signal"
        ],
        strategy_consensus=consensus
    )

    decision = DecisionEngine().decide(
        report
    )

    assert decision.action != "PREPARE_LONG"

def test_strategy_consensus_conflict_with_market_signal_blocks_long():

    memory = StrategyMemory()

    memory.store(
        {
            "strategy": "TREND_SELL_LOW",
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW",
            "samples": 50,
            "success_rate": 0.90,
            "score": 95,
            "status": "ACTIVE",
            "action": "SELL",
            "confidence": 90
        }
    )

    recall = StrategyRecall(memory)

    strategies = recall.recall(
        "TREND",
        "BUY",
        "LOW"
    )

    ranker = StrategyRanker()

    ranking_result = ranker.rank_with_result(
        strategies,
        market_context={
            "regime": "TREND",
            "signal": "BUY",
            "risk": "LOW"
        }
    )

    consensus = StrategyCouncil().evaluate(
        ranking_result
    )

    assert consensus.get("decision") == "SELL"

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="UP",
        regime="TREND",
        signal="BUY",
        confidence=90,
        risk="LOW",
        reasons=[
            "strategy consensus conflicts with market signal"
        ],
        strategy_consensus=consensus
    )

    decision = DecisionEngine().decide(
        report
    )

    assert decision.action != "PREPARE_LONG"

def test_strategy_consensus_conflict_with_market_signal_blocks_short():

    memory = StrategyMemory()

    memory.store(
        {
            "strategy": "TREND_BUY_LOW",
            "regime": "TREND",
            "signal": "SELL",
            "risk": "LOW",
            "samples": 50,
            "success_rate": 0.90,
            "score": 95,
            "status": "ACTIVE",
            "action": "BUY",
            "confidence": 90
        }
    )

    recall = StrategyRecall(memory)

    strategies = recall.recall(
        "TREND",
        "SELL",
        "LOW"
    )

    ranker = StrategyRanker()

    ranking_result = ranker.rank_with_result(
        strategies,
        market_context={
            "regime": "TREND",
            "signal": "SELL",
            "risk": "LOW"
        }
    )

    consensus = StrategyCouncil().evaluate(
        ranking_result
    )

    assert consensus.get("decision") == "BUY"

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="DOWN",
        regime="TREND",
        signal="SELL",
        confidence=90,
        risk="LOW",
        reasons=[
            "strategy consensus conflicts with market signal"
        ],
        strategy_consensus=consensus
    )

    decision = DecisionEngine().decide(
        report
    )

    assert decision.action != "PREPARE_SHORT"
    