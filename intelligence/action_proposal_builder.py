from intelligence.action_proposal import (
    ActionProposal
)



class ActionProposalBuilder:
    """
    Converts DecisionResult into
    an explainable action proposal.
    """



    def build(
        self,
        decision,
        report
    ):

        explanation = getattr(
            decision,
            "explanation",
            {}
        )


        strategy = (
            explanation.get(
                "dominant_strategy"
            )
            if explanation
            else None
        )


        risk_status = getattr(
            report,
            "risk",
            "UNKNOWN"
        )


        return ActionProposal(

            action=
                decision.action,

            symbol=
                report.symbol,

            strategy=
                strategy,

            confidence=
                decision.confidence,

            risk_status=
                risk_status,

            reason=
                decision.reason,

            metadata={

                "decision_explanation":
                    explanation
            }
        )