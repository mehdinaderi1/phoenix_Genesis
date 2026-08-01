from intelligence.lifecycle.lifecycle_intelligence_adapter import (
    LifecycleIntelligenceAdapter
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)



def test_intelligence_adapter_reads_strategy_lifecycle():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "champion_strategy",
            "ACTIVE",
            "CHAMPION",
            "promoted"
        )
    )


    adapter = LifecycleIntelligenceAdapter()


    result = adapter.analyze_strategy_lifecycle(
        history
    )


    assert result["strategy_state"] == "CHAMPION"

    assert result["lifecycle_action"] == "KEEP"

    assert result["governance"] == "APPROVED"



def test_intelligence_adapter_detects_improvement_need():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "active_strategy",
            "CANDIDATE",
            "ACTIVE",
            "activated"
        )
    )


    adapter = LifecycleIntelligenceAdapter()


    result = adapter.analyze_strategy_lifecycle(
        history
    )


    assert result["strategy_state"] == "ACTIVE"

    assert result["lifecycle_action"] == "IMPROVE"