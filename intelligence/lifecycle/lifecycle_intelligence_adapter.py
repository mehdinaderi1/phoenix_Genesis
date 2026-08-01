from intelligence.lifecycle.lifecycle_governance_bridge import (
    LifecycleGovernanceBridge
)


class LifecycleIntelligenceAdapter:


    def __init__(
        self,
        lifecycle_bridge=None
    ):

        self.lifecycle_bridge = (
            lifecycle_bridge
            if lifecycle_bridge
            else LifecycleGovernanceBridge()
        )


    def analyze_strategy_lifecycle(
        self,
        history
    ):

        result = self.lifecycle_bridge.process(
            history
        )


        return {

            "strategy_state":
                result["metrics"].current_state,

            "lifecycle_action":
                result["action"],

            "governance":
                result["governance"],

            "decision":
                result["decision"]

        }