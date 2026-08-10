from intelligence.experience_record import ExperienceRecord


class PerformanceLearningAdapter:

    def __init__(
        self,
        experience_memory
    ):

        self.experience_memory = experience_memory


    def process(
        self,
        performance
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


        experience = ExperienceRecord(

            regime="UNKNOWN",

            signal="UNKNOWN",

            risk="UNKNOWN",

            success=performance.success,

            score=score,

            strategy=performance.strategy

        )

        self.experience_memory.save_experience(
            experience
        )

        return {

            "outcome": outcome,

            "experience": experience

        }