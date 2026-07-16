class ExperienceContext:

    def __init__(self, memory):
        self.memory = memory


    def build_context(
        self,
        strategy
    ):

        experiences = self.memory.find_by_strategy(
            strategy
        )

        successful = [
            exp
            for exp in experiences
            if exp.success
        ]

        failed = [
            exp
            for exp in experiences
            if not exp.success
        ]

        return {

            "strategy": strategy,

            "total_experiences": len(experiences),

            "successful": len(successful),

            "failed": len(failed),

        }