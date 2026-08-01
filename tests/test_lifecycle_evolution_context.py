from intelligence.lifecycle.lifecycle_evolution_context import (
    LifecycleEvolutionContext
)

from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)

from intelligence.lifecycle.lifecycle_evolution_recall import (
    LifecycleEvolutionRecall
)


def build_context():

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

    recall = LifecycleEvolutionRecall(
        repository
    )

    return LifecycleEvolutionContext(
        recall
    )


def test_context_contains_history():

    context = build_context()

    result = context.build(
        "Strategy"
    )

    assert result["has_history"] is True
    assert result["evolution_count"] == 2


def test_context_returns_last_evolution():

    context = build_context()

    result = context.build(
        "Strategy"
    )

    assert result["last_evolution"]["version"] == "Strategy_v3"


def test_unknown_strategy_context():

    context = LifecycleEvolutionContext(
        LifecycleEvolutionRecall(
            LifecycleEvolutionRepository()
        )
    )

    result = context.build(
        "Unknown"
    )

    assert result["has_history"] is False
    assert result["evolution_count"] == 0


def test_previous_evolution_check():

    context = build_context()

    assert context.has_previous_evolution(
        "Strategy"
    ) is True