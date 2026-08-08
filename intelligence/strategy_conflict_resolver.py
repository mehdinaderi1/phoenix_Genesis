from intelligence.strategy_conflict import StrategyConflictResult


class StrategyConflictResolver:
    """
    Resolves strategy conflicts after conflict analysis.
    """

    MIN_CONFIDENCE = 0.6



    def resolve(
        self,
        conflict_result: StrategyConflictResult,
        consensus_confidence: float = 0.0
    ):

        if (
            conflict_result is None
        ):

            return {

                "resolution": "REJECT",

                "decision": None,

                "reason":
                    "No conflict analysis available"
            }



        if (
            conflict_result.conflict_level == "HIGH"
        ):

            return {

                "resolution": "HOLD",

                "decision": None,

                "reason":
                    "High strategy disagreement"
            }



        if (
            consensus_confidence
            <
            self.MIN_CONFIDENCE
        ):

            return {

                "resolution": "REJECT",

                "decision": None,

                "reason":
                    "Consensus confidence below threshold"
            }



        if (
            conflict_result.dominant_action
            is None
        ):

            return {

                "resolution": "HOLD",

                "decision": None,

                "reason":
                    "No dominant strategy"
            }



        if (
            conflict_result.conflict_level
            ==
            "MEDIUM"
        ):

            return {

                "resolution":
                    "ACCEPT_MAJORITY",

                "decision":
                    conflict_result.dominant_action,

                "reason":
                    "Majority strategy accepted with conflict"
            }



        return {

            "resolution":
                "ACCEPT",

            "decision":
                conflict_result.dominant_action,

            "reason":
                "Strategy agreement confirmed"
        }