from intelligence.governance.governance_service import (
    GovernanceService
)


class EvolutionGovernanceBridge:

    def __init__(
        self,
        governance_service=None,
        history=None
    ):

        if governance_service is None:
            governance_service = GovernanceService(
                history
            )

        self.governance_service = governance_service


    def evaluate(
        self,
        evolution_result
    ):

        governance_result = (
            self.governance_service.evaluate(
                evolution_result
            )
        )


        return {

            "evolution": evolution_result,

            "governance": governance_result,

            "approved":
                governance_result.get(
                    "status"
                )
                == "APPROVED"

        }