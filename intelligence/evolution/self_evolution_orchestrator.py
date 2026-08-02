class SelfEvolutionOrchestrator:


    def __init__(
        self,
        awareness,
        governor,
        policy
    ):

        self.awareness = awareness

        self.governor = governor

        self.policy = policy



    def evaluate(
        self,
        strategy
    ):

        awareness_result = (
            self.awareness.evaluate(
                strategy
            )
        )


        governor_result = (
            self.governor.decide(
                awareness_result
            )
        )


        policy_input = {

            **awareness_result,

            "decision":
                governor_result["decision"],

        }


        policy_result = (
            self.policy.evaluate(
                policy_input
            )
        )


        allowed = (

            governor_result["decision"]
            ==
            "APPROVE"

            and

            policy_result["allowed"]

        )


        return {

            "allowed":
                allowed,

            "awareness":
                awareness_result,

            "governor":
                governor_result,

            "policy":
                policy_result

        }