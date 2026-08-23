from intelligence.experience_record import ExperienceRecord


class PerformanceLearningAdapter:

    def __init__(
        self,
        experience_memory
    ):

        self.experience_memory = experience_memory


    def process(
        self,
        performance,
        decision=None
    ):

        outcome = (
            "SUCCESS"
            if performance.success
            else
            "FAILED"
        )


        score = (
            100
            if performance.success
            else
            0
        )


        if decision is None:

            regime = "UNKNOWN"

            signal = "UNKNOWN"

            risk = "UNKNOWN"

            decision_action = None

            confidence = 0

            trace = {}

            champion_strategy = None

        else:

            regime = getattr(
                decision,
                "regime",
                "UNKNOWN"
            )

            signal = getattr(
                decision,
                "signal",
                "UNKNOWN"
            )

            risk = getattr(
                decision,
                "risk",
                "UNKNOWN"
            )

            decision_action = getattr(
                decision,
                "action",
                None
            )

            confidence = getattr(
                decision,
                "confidence",
                0
            )

            trace = getattr(
                decision,
                "trace",
                {}
            )

            champion_strategy = getattr(
                decision,
                "champion_strategy",
                None
            )


        experience = ExperienceRecord(

            regime=regime,

            signal=signal,

            risk=risk,

            success=performance.success,

            score=score,

            decision=decision_action,

            strategy=performance.strategy,

            confidence=confidence,

            trace=trace,

            champion_strategy=champion_strategy

        )


        self.experience_memory.save_experience(
            experience
        )


        return {

            "outcome": outcome,

            "experience": experience

        }