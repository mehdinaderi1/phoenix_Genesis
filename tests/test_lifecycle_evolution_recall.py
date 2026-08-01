from intelligence.lifecycle.lifecycle_evolution_recall import (
    LifecycleEvolutionRecall
)

from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)


def build_recall():

    repository = LifecycleEvolutionRepository()

    repository.save({
        "strategy": "Strategy",
        "action": "IMPROVE",
        "version": "Strategy_v2"
    })

    repository.save({
        "strategy": "Strategy",
        "action": "IMPROVE",
        "version": "Strategy_v3"
    })

    return LifecycleEvolutionRecall(
        repository
    )


def test_recall_strategy_history():

    recall = build_recall()

    history = recall.recall(
        "Strategy"
    )

    assert len(history) == 2


def test_latest_evolution_returned():

    recall = build_recall()

    latest = recall.latest(
        "Strategy"
    )

    assert latest["version"] == "Strategy_v3"


def test_has_evolved_returns_true():

    recall = build_recall()

    assert recall.has_evolved(
        "Strategy"
    )


def test_unknown_strategy_has_no_history():

    recall = build_recall()

    assert recall.has_evolved(
        "UnknownStrategy"
    ) is False