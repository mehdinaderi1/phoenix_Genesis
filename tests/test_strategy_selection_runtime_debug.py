from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_strategy_selection_runtime_debug():

    flow = IntelligenceFlow()

    strategy = {
        "name": "trend_following",
        "strategy": "trend_following",
        "regime": "BULLISH",
        "signal": "BUY",
        "risk": "LOW",
        "score": 90,
        "success_rate": 0.85,
        "samples": 10,
        "status": "ACTIVE",
    }

    flow.strategy_memory.store(strategy)

    print("\n=== STRATEGY SELECTION RUNTIME DEBUG ===")

    print("\nMEMORY:")
    print(flow.strategy_memory.records)

    recalled = flow.strategy_recall.recall(
        "BULLISH",
        "BUY",
        "LOW",
    )

    print("\nRECALLED:")
    print(recalled)

    ranking = flow.strategy_ranker.rank_with_result(
        recalled,
        market_context={
            "regime": "BULLISH",
            "signal": "BUY",
            "risk": "LOW",
        },
    )

    print("\nRANKING:")
    print(ranking)

    print("\nTOP STRATEGY:")
    print(ranking.top_strategy)

    if ranking.top_strategy:
        print("\nTOP RECORD:")
        print(ranking.top_strategy.strategy_record)

    selected = flow.strategy_selector.select_with_result(
        "BULLISH",
        "BUY",
        "LOW",
    )

    print("\nSELECTED:")
    print(selected)

    if selected:
        print("\nSELECTED CHAMPION:")
        print(selected["champion"])

    assert recalled
    assert ranking.top_strategy is not None
    assert ranking.top_strategy.strategy_record is not None
    assert selected is not None
    assert selected["champion"] is not None


def test_flow_strategy_selection_debug():

    flow = IntelligenceFlow()

    flow.strategy_memory.store({
        "name": "trend_following",
        "strategy": "trend_following",
        "regime": "BULLISH",
        "signal": "BUY",
        "risk": "LOW",
        "score": 90,
        "success_rate": 0.85,
        "samples": 10,
        "status": "ACTIVE",
    })

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85,
    )

    report = flow.create_report(consensus)

    print("\n=== FLOW STRATEGY DEBUG ===")
    print("REPORT REGIME:", report.regime)
    print("REPORT SIGNAL:", report.signal)
    print("REPORT RISK:", report.risk)
    print("CHAMPION:", report.champion_strategy)
    print("STRATEGY RANKING:", report.strategy_ranking)
    print("DECISION:", report.decision)
    print("STRATEGY INSIGHT:", report.strategy_insight)
    print("STRATEGY PERFORMANCE:", report.strategy_performance)