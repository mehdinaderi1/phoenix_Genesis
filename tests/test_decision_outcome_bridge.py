from intelligence.decision_outcome_bridge import DecisionOutcomeBridge

from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.performance_feedback import PerformanceFeedback
from intelligence.memory.strategy_performance_memory import (
    StrategyPerformanceMemory
)

from intelligence.decision_record import DecisionRecord


def test_decision_outcome_bridge_long_success():

    bridge = DecisionOutcomeBridge(
        outcome_memory=OutcomeMemory(),
        performance_feedback=PerformanceFeedback(),
        strategy_performance_memory=(
            StrategyPerformanceMemory()
        )
    )


    decision = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="30m",

        regime="BULL",

        signal="LONG",

        confidence=80,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED",

        champion_strategy={
            "name": "momentum_strategy"
        }

    )


    result = bridge.process(
        decision,
        entry_price=60000,
        exit_price=61000
    )


    assert result["result"] == "SUCCESS"

    assert result["score"] == 100


def test_decision_outcome_bridge_saves_outcome():

    outcome_memory = OutcomeMemory()


    bridge = DecisionOutcomeBridge(

        outcome_memory=outcome_memory,

        performance_feedback=PerformanceFeedback(),

        strategy_performance_memory=(
            StrategyPerformanceMemory()
        )

    )


    decision = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="30m",

        regime="BULL",

        signal="LONG",

        confidence=80,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED"

    )


    bridge.process(
        decision,
        entry_price=60000,
        exit_price=61000
    )


    assert len(
        outcome_memory.records
    ) == 1


def test_decision_outcome_bridge_updates_strategy_memory():

    strategy_memory = StrategyPerformanceMemory()


    bridge = DecisionOutcomeBridge(

        outcome_memory=OutcomeMemory(),

        performance_feedback=PerformanceFeedback(),

        strategy_performance_memory=strategy_memory

    )


    decision = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="30m",

        regime="BULL",

        signal="LONG",

        confidence=80,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED",

        champion_strategy={
            "name": "momentum_strategy"
        }

    )


    bridge.process(

        decision,

        entry_price=60000,

        exit_price=61000

    )


    performances = (
        strategy_memory.get_performances()
    )


    assert len(
        performances
    ) == 1


    assert (
        performances[0].strategy
        ==
        "momentum_strategy"
    )


    assert (
        performances[0].success
        is True
    )

def test_decision_outcome_bridge_updates_experience_memory():

    from intelligence.memory.experience_memory import (
        ExperienceMemory
    )

    from intelligence.performance_learning_adapter import (
        PerformanceLearningAdapter
    )


    experience_memory = ExperienceMemory()

    strategy_memory = StrategyPerformanceMemory()

    bridge = DecisionOutcomeBridge(

        outcome_memory=OutcomeMemory(),

        performance_feedback=PerformanceFeedback(),

        strategy_performance_memory=strategy_memory,

        performance_learning=PerformanceLearningAdapter(
            experience_memory=experience_memory
        )

    )


    decision = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="30m",

        regime="BULL",

        signal="LONG",

        confidence=80,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED",

        champion_strategy={
            "name": "momentum_strategy"
        }

    )


    result = bridge.process(

        decision,

        entry_price=60000,

        exit_price=61000

    )


    assert result["result"] == "SUCCESS"

    assert len(
        experience_memory.records
    ) == 1

    assert (
        experience_memory.records[0].strategy
        ==
        "momentum_strategy"
    )

    assert (
        experience_memory.records[0].success
        is True
    )


def test_decision_outcome_bridge_preserves_decision_context_in_learning():

    from intelligence.memory.experience_memory import (
        ExperienceMemory
    )

    from intelligence.performance_learning_adapter import (
        PerformanceLearningAdapter
    )


    experience_memory = ExperienceMemory()


    bridge = DecisionOutcomeBridge(

        outcome_memory=OutcomeMemory(),

        performance_feedback=PerformanceFeedback(),

        strategy_performance_memory=(
            StrategyPerformanceMemory()
        ),

        performance_learning=(
            PerformanceLearningAdapter(
                experience_memory=experience_memory
            )
        )
    )


    decision = DecisionRecord(

        symbol="BTCUSDT",

        timeframe="30m",

        regime="BULL",

        signal="LONG",

        confidence=85,

        risk="LOW",

        action="PREPARE_LONG",

        validation_status="APPROVED",

        champion_strategy={
            "name": "momentum_strategy"
        },

        trace={
            "source": "decision_engine"
        }
    )


    result = bridge.process(

        decision,

        entry_price=60000,

        exit_price=61000
    )


    experience = (
        experience_memory.records[0]
    )


    assert result["result"] == "SUCCESS"

    assert experience.regime == "BULL"

    assert experience.signal == "LONG"

    assert experience.risk == "LOW"

    assert experience.decision == (
        "PREPARE_LONG"
    )

    assert experience.confidence == 85

    assert experience.strategy == (
        "momentum_strategy"
    )

    assert experience.champion_strategy == {
        "name": "momentum_strategy"
    }

    assert experience.trace == {
        "source": "decision_engine"
    }