from intelligence.lifecycle.lifecycle_governance_bridge import (
    LifecycleGovernanceBridge
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)


class AllowGovernance:


    def check(self, action):

        return True



class BlockGovernance:


    def check(self, action):

        return False



def test_governance_allows_lifecycle_action():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "champion_strategy",
            "ACTIVE",
            "CHAMPION",
            "promoted"
        )
    )


    bridge = LifecycleGovernanceBridge(
        governance_gate=AllowGovernance()
    )


    result = bridge.process(
        history
    )


    assert result["action"] == "KEEP"

    assert result["governance"] == "APPROVED"



def test_governance_blocks_lifecycle_action():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "active_strategy",
            "CANDIDATE",
            "ACTIVE",
            "activated"
        )
    )


    bridge = LifecycleGovernanceBridge(
        governance_gate=BlockGovernance()
    )


    result = bridge.process(
        history
    )


    assert result["action"] == "IMPROVE"

    assert result["governance"] == "BLOCKED"