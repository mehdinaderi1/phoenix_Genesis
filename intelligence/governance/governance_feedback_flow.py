from intelligence.governance.governance_feedback import (
    GovernanceFeedback
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_trust import (
    GovernanceTrust
)


class GovernanceFeedbackFlow:


    def __init__(
        self,
        feedback=None,
        trust=None,
        memory=None
    ):


        self.memory = (
            memory
            or GovernanceMemory()
        )


        self.feedback = (
            feedback
            or GovernanceFeedback(
                self.memory
            )
        )


        self.trust = (
            trust
            or GovernanceTrust()
        )



    def process(
        self,
        strategy,
        result
    ):


        feedback = self.feedback.record(
            strategy,
            result
        )


        success_rate = (
            self.feedback.success_rate()
        )


        trust = self.trust.calculate(
            success_rate
        )


        return {

            "strategy": strategy,

            "feedback": feedback,

            "success_rate": success_rate,

            "trust": trust

        }