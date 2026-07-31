from intelligence.evolution.evolution_governance_bridge import (
    EvolutionGovernanceBridge
)


class MockGovernance:

    def __init__(self, status="APPROVED"):
        self.status = status


    def evaluate(self, evolution_result):

        return {
            "status": self.status,
            "reason": "mock governance"
        }



def test_evolution_governance_bridge_approved():

    bridge = EvolutionGovernanceBridge(
        governance_service=MockGovernance()
    )


    result = bridge.evaluate(
        {
            "action": "EVOLVE",
            "strategy": "scalp_alpha_v2"
        }
    )


    assert result["approved"] is True

    assert (
        result["governance"]["status"]
        ==
        "APPROVED"
    )



def test_evolution_governance_bridge_blocked():

    bridge = EvolutionGovernanceBridge(
        governance_service=MockGovernance(
            status="REJECTED"
        )
    )


    result = bridge.evaluate(
        {
            "action": "EVOLVE",
            "strategy": "bad_strategy"
        }
    )


    assert result["approved"] is False

    assert (
        result["governance"]["status"]
        ==
        "REJECTED"
    )