from intelligence.decision import DecisionResult
from intelligence.decision_outcome_bridge import (
    DecisionOutcomeBridge
)
from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.memory.strategy_performance_memory import (
    StrategyPerformanceMemory
)
from intelligence.performance_feedback import PerformanceFeedback
from intelligence.performance_learning_adapter import (
    PerformanceLearningAdapter
)
from intelligence.memory.experience_memory import ExperienceMemory


def test_champion_strategy_survives_decision_outcome_experience_cycle():

    # -------------------------------------------------
    # 1. Champion Strategy
    # -------------------------------------------------

    champion = {
        "name": "trend_following",
        "strategy": "trend_following",
        "regime": "TRENDING_BULLISH",
        "signal": "BUY",
        "risk": "LOW",
        "score": 85,
        "success_rate": 0.85,
        "status": "ACTIVE",
    }


    # -------------------------------------------------
    # 2. Decision
    # -------------------------------------------------

    decision = DecisionResult(

        action="PREPARE_LONG",

        reason="Strong bullish signal",

        confidence=85,

        regime="TRENDING_BULLISH",

        signal="BUY",

        risk="LOW",

        champion_strategy=champion,

        metadata={
            "champion_strategy": champion
        }
    )


    # -------------------------------------------------
    # 3. Memories / Learning
    # -------------------------------------------------

    outcome_memory = OutcomeMemory()

    strategy_performance_memory = (
        StrategyPerformanceMemory()
    )

    experience_memory = ExperienceMemory()

    performance_feedback = PerformanceFeedback()

    performance_learning = (
        PerformanceLearningAdapter(
            experience_memory
        )
    )


    # -------------------------------------------------
    # 4. Decision → Outcome Bridge
    # -------------------------------------------------

    bridge = DecisionOutcomeBridge(

        outcome_memory=outcome_memory,

        performance_feedback=performance_feedback,

        strategy_performance_memory=(
            strategy_performance_memory
        ),

        performance_learning=performance_learning
    )


    result = bridge.process(

        decision=decision,

        entry_price=65000,

        exit_price=67000
    )


    # -------------------------------------------------
    # 5. Performance Identity
    # -------------------------------------------------

    performance = result["performance"]

    assert performance is not None

    assert performance.strategy == (
        champion["name"]
    )


    # -------------------------------------------------
    # 6. Experience Identity
    # -------------------------------------------------

    learning = result["performance_learning"]

    assert learning is not None

    experience = learning["experience"]

    assert experience.strategy == (
        champion["name"]
    )


    # -------------------------------------------------
    # 7. Champion Identity
    # -------------------------------------------------

    assert experience.champion_strategy == (
        champion
    )


    # -------------------------------------------------
    # 8. Memory Persistence
    # -------------------------------------------------

    assert len(
        outcome_memory.records
    ) == 1

    assert len(
        strategy_performance_memory.records
    ) == 1

    assert len(
        experience_memory.records
    ) == 1