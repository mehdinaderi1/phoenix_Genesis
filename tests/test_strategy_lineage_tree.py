from intelligence.lifecycle.strategy_lineage_tracker import (
    StrategyLineageTracker
)


def test_strategy_lineage_tree_creation():

    tracker = StrategyLineageTracker()

    tracker.register(
        "MomentumStrategy"
    )

    tracker.register(
        "MomentumStrategy_v2",
        parent_strategy="MomentumStrategy",
        generation=1
    )

    tracker.register(
        "MomentumStrategy_v3",
        parent_strategy="MomentumStrategy_v2",
        generation=2
    )


    assert tracker.get_parent(
        "MomentumStrategy_v3"
    ) == "MomentumStrategy_v2"


    assert tracker.get_children(
        "MomentumStrategy"
    ) == [
        "MomentumStrategy_v2"
    ]


    assert tracker.get_ancestry(
        "MomentumStrategy_v3"
    ) == [
        "MomentumStrategy_v3",
        "MomentumStrategy_v2",
        "MomentumStrategy"
    ]