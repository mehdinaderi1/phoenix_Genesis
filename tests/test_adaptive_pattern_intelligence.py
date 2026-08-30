from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_record import ExperienceRecord


def make_experience(
    strategy,
    success,
    score
):
    return ExperienceRecord(
        regime="TREND",
        signal="BUY",
        risk="LOW",
        success=success,
        score=score,
        decision="PREPARE_LONG",
        strategy=strategy,
        confidence=80,
        trace={},
        champion_strategy={
            "name": strategy
        }
    )


def test_pattern_intelligence_preserves_strategy_performance():

    memory = ExperienceMemory()

    for _ in range(8):

        memory.save_experience(
            make_experience(
                "strategy_A",
                True,
                80
            )
        )

    for _ in range(2):

        memory.save_experience(
            make_experience(
                "strategy_A",
                False,
                40
            )
        )

    for _ in range(5):

        memory.save_experience(
            make_experience(
                "strategy_B",
                True,
                60
            )
        )

    for _ in range(5):

        memory.save_experience(
            make_experience(
                "strategy_B",
                False,
                40
            )
        )

    intelligence = PatternIntelligence()

    insights = intelligence.analyze(
        memory.get_experiences()
    )

    assert len(insights) == 1

    insight = insights[0]

    assert insight["pattern"] == (
        "TREND",
        "BUY",
        "LOW"
    )

    assert insight["samples"] == 20

    assert "strategies" in insight

    assert "strategy_A" in insight["strategies"]

    assert "strategy_B" in insight["strategies"]

    assert (
        insight["strategies"]["strategy_A"]["samples"]
        == 10
    )

    assert (
        insight["strategies"]["strategy_B"]["samples"]
        == 10
    )

    assert (
        insight["strategies"]["strategy_A"]["success_rate"]
        == 0.8
    )

    assert (
        insight["strategies"]["strategy_B"]["success_rate"]
        == 0.5
    )

    assert (
        insight["best_strategy"]
        == "strategy_A"
    )
