from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_record import ExperienceRecord


def make_experience(strategy, success):
    return ExperienceRecord(
        regime="TRENDING",
        signal="BUY",
        risk="LOW",
        success=success,
        score=90 if success else 20,
        strategy=strategy,
    )


def test_records_and_get_experiences_share_same_collection():

    memory = ExperienceMemory()

    experience = make_experience(
        "trend_following",
        True
    )

    memory.save_experience(
        experience
    )

    assert memory.records is (
        memory.get_experiences()
    )

    assert memory.records[0] is (
        memory.get_experiences()[0]
    )


def test_find_by_strategy_returns_matching_experiences():

    memory = ExperienceMemory()

    first = make_experience(
        "trend_following",
        True
    )

    second = make_experience(
        "mean_reversion",
        True
    )

    memory.save_experience(first)
    memory.save_experience(second)

    results = memory.find_by_strategy(
        "trend_following"
    )

    assert len(results) == 1
    assert results[0] is first


def test_find_similar_filters_by_strategy_and_success():

    memory = ExperienceMemory()

    success = make_experience(
        "trend_following",
        True
    )

    failure = make_experience(
        "trend_following",
        False
    )

    other_strategy = make_experience(
        "mean_reversion",
        True
    )

    memory.save_experience(success)
    memory.save_experience(failure)
    memory.save_experience(other_strategy)

    results = memory.find_similar(
        "trend_following",
        success=True
    )

    assert len(results) == 1
    assert results[0] is success


def test_find_similar_without_success_filter_returns_all_matching_strategy():

    memory = ExperienceMemory()

    success = make_experience(
        "trend_following",
        True
    )

    failure = make_experience(
        "trend_following",
        False
    )

    memory.save_experience(success)
    memory.save_experience(failure)

    results = memory.find_similar(
        "trend_following"
    )

    assert len(results) == 2
    assert results[0] is success
    assert results[1] is failure