from intelligence.lifecycle.lifecycle_governance_gate import (
    LifecycleGovernanceGate
)

from intelligence.learning.strategy_version import (
    StrategyVersion
)



class MockGovernance:


    def __init__(self, status):

        self.status = status



    def evaluate(self, strategy):

        return {

            "status": self.status,

            "reason": "governance decision"

        }



def test_governance_allows_activation():


    strategy = StrategyVersion(
        name="trend_strategy_v2"
    )


    gate = LifecycleGovernanceGate(
        MockGovernance("APPROVED")
    )


    result = gate.approve_activation(
        strategy
    )


    assert result["allowed"] is True



def test_governance_blocks_activation():


    strategy = StrategyVersion(
        name="bad_strategy_v2"
    )


    gate = LifecycleGovernanceGate(
        MockGovernance("BLOCKED")
    )


    result = gate.approve_activation(
        strategy
    )


    assert result["allowed"] is False