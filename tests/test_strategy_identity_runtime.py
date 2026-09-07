from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_runtime_strategy_identity_drift():

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

    champion_name = None

    if report.champion_strategy:
        champion_name = report.champion_strategy.get("name")

    decision_action = report.decision.action
    strategy_insight_identity = (
        report.strategy_insight["strategy"]
    )

    champion_history = (
        flow.strategy_history.get_history(
            champion_name
        )
        if champion_name
        else []
    )

    action_history = (
        flow.strategy_history.get_history(
            decision_action
        )
    )

    print("\nCHAMPION:", champion_name)
    print("DECISION ACTION:", decision_action)
    print(
        "STRATEGY INSIGHT:",
        strategy_insight_identity
    )
    print(
        "CHAMPION HISTORY:",
        champion_history
    )
    print(
        "ACTION HISTORY:",
        action_history
    )
    print(
        "STRATEGY PERFORMANCE:",
        report.strategy_performance
    )

    assert champion_name == "trend_following"
    assert decision_action == "PREPARE_LONG"
    assert strategy_insight_identity == decision_action
    assert champion_history != []
    assert action_history == []