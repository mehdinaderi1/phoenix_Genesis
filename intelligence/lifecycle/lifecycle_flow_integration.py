from intelligence.lifecycle.lifecycle_intelligence_adapter import (
    LifecycleIntelligenceAdapter
)


class LifecycleFlowIntegration:


    def __init__(
        self,
        lifecycle_adapter=None
    ):

        self.lifecycle_adapter = (
            lifecycle_adapter
            if lifecycle_adapter
            else LifecycleIntelligenceAdapter()
        )



    def enrich(
        self,
        flow_result,
        history
    ):

        lifecycle_result = (
            self.lifecycle_adapter.analyze_strategy_lifecycle(
                history
            )
        )


        flow_result["lifecycle"] = lifecycle_result


        return flow_result