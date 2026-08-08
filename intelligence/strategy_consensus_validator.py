class StrategyConsensusValidator:


    def validate(
        self,
        consensus
    ):

        if consensus is None:
            return False


        return (
            consensus.get(
                "supporting_strategies",
                0
            )
            >
            consensus.get(
                "opposing_strategies",
                0
            )
        )


    def explain(
        self,
        consensus
    ):

        allowed = self.validate(
            consensus
        )


        return {
            "allowed": allowed,

            "supporting_strategies": (
                consensus.get(
                    "supporting_strategies",
                    0
                )
                if consensus
                else 0
            ),

            "opposing_strategies": (
                consensus.get(
                    "opposing_strategies",
                    0
                )
                if consensus
                else 0
            ),

            "decision": (
                consensus.get(
                    "decision"
                )
                if consensus
                else None
            )
        }