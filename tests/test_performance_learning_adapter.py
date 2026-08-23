from intelligence.performance_learning_adapter import (
    PerformanceLearningAdapter
)

from intelligence.performance_record import (
    PerformanceRecord
)

from intelligence.memory.experience_memory import (
    ExperienceMemory
)


def test_performance_learning_adapter_success_creates_experience():

    experience_memory = ExperienceMemory()


    adapter = PerformanceLearningAdapter(
        experience_memory=experience_memory
    )


    performance = PerformanceRecord(

        strategy="momentum_strategy",

        profit_loss=1000,

        success=True

    )


    result = adapter.process(
        performance
    )


    assert result["outcome"] == "SUCCESS"


    assert len(
        experience_memory.records
    ) == 1



def test_performance_learning_adapter_failure_creates_experience():

    experience_memory = ExperienceMemory()


    adapter = PerformanceLearningAdapter(
        experience_memory=experience_memory
    )


    performance = PerformanceRecord(

        strategy="breakout_strategy",

        profit_loss=-500,

        success=False

    )


    result = adapter.process(
        performance
    )


    assert result["outcome"] == "FAILED"


    assert len(
        experience_memory.records
    ) == 1



def test_performance_learning_adapter_keeps_strategy_context():

    experience_memory = ExperienceMemory()


    adapter = PerformanceLearningAdapter(
        experience_memory=experience_memory
    )


    performance = PerformanceRecord(

        strategy="trend_strategy",

        profit_loss=250,

        success=True

    )


    adapter.process(
        performance
    )


    experience = (
        experience_memory.records[0]
    )


    assert (
        experience.strategy
        ==
        "trend_strategy"
    )

def test_performance_learning_adapter_preserves_multiple_experiences():

    experience_memory = ExperienceMemory()

    adapter = PerformanceLearningAdapter(
        experience_memory=experience_memory
    )

    adapter.process(
        PerformanceRecord(
            strategy="momentum_strategy",
            profit_loss=1000,
            success=True
        )
    )

    adapter.process(
        PerformanceRecord(
            strategy="momentum_strategy",
            profit_loss=-500,
            success=False
        )
    )

    experiences = experience_memory.find_by_strategy(
        "momentum_strategy"
    )

    assert len(experiences) == 2

    assert experiences[0].success is True
    assert experiences[1].success is False


from intelligence.decision_record import DecisionRecord


def test_performance_learning_adapter_preserves_decision_context():

    experience_memory = ExperienceMemory()

    adapter = PerformanceLearningAdapter(
        experience_memory=experience_memory
    )

    performance = PerformanceRecord(
        strategy="momentum_strategy",
        profit_loss=1000,
        success=True
    )

    decision = DecisionRecord(
        symbol="BTCUSDT",
        timeframe="30m",
        regime="BULL",
        signal="BUY",
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

    result = adapter.process(
        performance,
        decision
    )

    experience = (
        experience_memory.records[0]
    )

    assert result["outcome"] == "SUCCESS"

    assert experience.regime == "BULL"
    assert experience.signal == "BUY"
    assert experience.risk == "LOW"

    assert experience.decision == "PREPARE_LONG"

    assert experience.strategy == (
        "momentum_strategy"
    )

    assert experience.confidence == 85

    assert experience.champion_strategy == {
        "name": "momentum_strategy"
    }

    assert experience.trace == {
        "source": "decision_engine"
    }