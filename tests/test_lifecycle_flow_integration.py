from intelligence.lifecycle.lifecycle_flow_integration import (
    LifecycleFlowIntegration
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)



def test_flow_integration_adds_lifecycle_information():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "champion_strategy",
            "ACTIVE",
            "CHAMPION",
            "promoted"
        )
    )


    flow_result = {

        "decision": "BUY",

        "confidence": 90

    }


    integration = LifecycleFlowIntegration()


    result = integration.enrich(
        flow_result,
        history
    )


    assert "lifecycle" in result

    assert result["lifecycle"]["strategy_state"] == "CHAMPION"

    assert result["lifecycle"]["lifecycle_action"] == "KEEP"



def test_flow_integration_detects_improvement_state():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "active_strategy",
            "CANDIDATE",
            "ACTIVE",
            "activated"
        )
    )


    flow_result = {

        "decision": "WAIT",

        "confidence": 60

    }


    integration = LifecycleFlowIntegration()


    result = integration.enrich(
        flow_result,
        history
    )


    assert result["lifecycle"]["strategy_state"] == "ACTIVE"

    assert result["lifecycle"]["lifecycle_action"] == "IMPROVE"