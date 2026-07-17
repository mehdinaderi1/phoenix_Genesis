from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_record import ExperienceRecord
from intelligence.experience_analyzer import ExperienceAnalyzer


def test_experience_pattern_analysis():

    memory = ExperienceMemory()

    memory.save_experience(
        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            True,
            8
        )
    )

    memory.save_experience(
        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            True,
            6
        )
    )

    memory.save_experience(
        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            False,
            -3
        )
    )


    analyzer = ExperienceAnalyzer(memory)

    patterns = analyzer.analyze()


    assert len(patterns) == 1

    pattern = patterns[0]

    assert pattern["samples"] == 3

    assert pattern["success_rate"] == 0.67

    assert pattern["avg_score"] == 3.67