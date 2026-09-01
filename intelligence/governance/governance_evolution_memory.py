from intelligence.governance.governance_memory import (
    GovernanceMemory
)


class GovernanceEvolutionMemory:


    def __init__(
        self,
        memory=None
    ):

        if memory is None:
            memory = GovernanceMemory()

        self.memory = memory


    def store(
        self,
        strategy,
        decision,
        score
    ):

        record = {
            "strategy": strategy,
            "decision": decision,
            "score": score
        }


        self.memory.store(
            record
        )


        return record



    def count(
        self
    ):

        return self.memory.count()



    def history(
        self
    ):

        return self.memory.get_all()