from intelligence.lifecycle.lifecycle_orchestrator import (
    LifecycleOrchestrator
)


class LifecycleEvolutionBridge:


    def __init__(
        self,
        orchestrator=None
    ):

        self.orchestrator = (
            orchestrator
            if orchestrator
            else LifecycleOrchestrator()
        )


    def process(self, history):

        result = self.orchestrator.run(
            history
        )

        action = result["decision"].action


        if action == "KEEP":

            outcome = "KEEP_STRATEGY"


        elif action == "IMPROVE":

            outcome = "SEND_TO_IMPROVEMENT"


        elif action == "ARCHIVE":

            outcome = "ARCHIVE_STRATEGY"


        elif action == "EVALUATE":

            outcome = "EVALUATE_STRATEGY"


        else:

            outcome = "UNKNOWN"


        return {

            "action": action,

            "outcome": outcome,

            "metrics": result["metrics"],

            "decision": result["decision"]

        }