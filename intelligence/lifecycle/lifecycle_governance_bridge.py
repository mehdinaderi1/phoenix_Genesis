from intelligence.lifecycle.lifecycle_orchestrator import (
    LifecycleOrchestrator
)


class LifecycleGovernanceBridge:


    def __init__(
        self,
        orchestrator=None,
        governance_gate=None
    ):

        self.orchestrator = (
            orchestrator
            if orchestrator
            else LifecycleOrchestrator()
        )

        self.governance_gate = governance_gate



    def process(self, history):

        result = self.orchestrator.run(
            history
        )


        decision = result["decision"]

        action = decision.action


        if self.governance_gate:

            approved = self.governance_gate.check(
                action
            )

        else:

            approved = True



        if approved:

            outcome = "APPROVED"

        else:

            outcome = "BLOCKED"



        return {

            "action": action,

            "governance": outcome,

            "metrics": result["metrics"],

            "decision": decision

        }