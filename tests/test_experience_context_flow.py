from intelligence.experience_context import ExperienceContext
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.performance_record import PerformanceRecord


def test_experience_context_should_find_previous_experiences():

    memory = ExperienceMemory()

    memory.save_experience(
        PerformanceRecord(
            strategy="Trend",
            profit_loss=2.5,
            success=True
        )
    )

    memory.save_experience(
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False
        )
    )

    context = ExperienceContext(
        memory=memory
    )

    result = context.build_context(
        strategy="Trend"
    )

    assert result["total_experiences"] == 2
    assert result["successful"] == 1
    assert result["failed"] == 1


def test_experience_context_empty_memory():

    memory = ExperienceMemory()

    context = ExperienceContext(
        memory=memory
    )

    result = context.build_context(
        strategy="Trend"
    )

    assert result["total_experiences"] == 0