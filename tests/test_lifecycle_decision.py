from intelligence.lifecycle.lifecycle_decision import (
    LifecycleDecisionEngine
)

from intelligence.lifecycle.lifecycle_metrics import (
    LifecycleMetrics
)



def test_champion_strategy_keep_decision():

    metrics = LifecycleMetrics(

        strategy_name="champion_strategy",

        total_events=5,

        transitions=5,

        current_state="CHAMPION",

        lifecycle_score=100,

        health="EXCELLENT"

    )


    engine = LifecycleDecisionEngine()


    result = engine.decide(
        metrics
    )


    assert result.action == "KEEP"

    assert result.score == 100



def test_active_strategy_improve_decision():

    metrics = LifecycleMetrics(

        strategy_name="active_strategy",

        total_events=2,

        transitions=2,

        current_state="ACTIVE",

        lifecycle_score=20,

        health="GOOD"

    )


    engine = LifecycleDecisionEngine()


    result = engine.decide(
        metrics
    )


    assert result.action == "IMPROVE"

    assert result.score == 20



def test_retired_strategy_archive_decision():

    metrics = LifecycleMetrics(

        strategy_name="old_strategy",

        total_events=4,

        transitions=4,

        current_state="RETIRED",

        lifecycle_score=60,

        health="ENDED"

    )


    engine = LifecycleDecisionEngine()


    result = engine.decide(
        metrics
    )


    assert result.action == "ARCHIVE"



def test_candidate_strategy_evaluation_decision():

    metrics = LifecycleMetrics(

        strategy_name="new_strategy",

        total_events=1,

        transitions=1,

        current_state="CANDIDATE",

        lifecycle_score=20,

        health="STABLE"

    )


    engine = LifecycleDecisionEngine()


    result = engine.decide(
        metrics
    )


    assert result.action == "EVALUATE"