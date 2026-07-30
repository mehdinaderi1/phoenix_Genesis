from intelligence.learning.strategy_version import StrategyVersion
from intelligence.governance.strategy_lifecycle import StrategyLifecycle
from intelligence.governance.strategy_governor import StrategyGovernor


class GovernanceFlow:


    def __init__(self):

        self.lifecycle = StrategyLifecycle()

        self.governor = StrategyGovernor()



    def process(
        self,
        strategy: StrategyVersion
    ):

        # Step 1: Create lifecycle entry

        self.lifecycle.create(strategy)


        # Step 2: Move to candidate

        self.lifecycle.promote_candidate(strategy)


        # Step 3: Governance evaluation

        decision = self.governor.evaluate(strategy)


        if decision == "APPROVED":

            self.lifecycle.activate(strategy)

            self.lifecycle.promote_champion(strategy)


        elif decision == "ARCHIVED":

            self.lifecycle.archive(strategy)


        else:

            strategy.status = "REVIEW"


        return {

            "decision": decision,

            "strategy": strategy

        }