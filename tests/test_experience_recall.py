from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_record import ExperienceRecord


def test_phoenix_can_recall_experience():

    memory = ExperienceMemory()


    experience = ExperienceRecord(
        regime="TRENDING",
        signal="BUY",
        risk="LOW",
        success=True,
        score=90
    )


    memory.save_experience(
        experience
    )


    results = memory.get_experiences()


    assert len(results) == 1

    assert results[0].signal == "BUY"

    assert results[0].success is True