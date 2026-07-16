from intelligence.performance_record import PerformanceRecord


class ExperienceMemory:

    def __init__(self):
        self.experiences = []

    def save_experience(
        self,
        experience: PerformanceRecord
    ):
        self.experiences.append(experience)

    def get_experiences(self):
        return self.experiences

    def find_by_strategy(
        self,
        strategy: str
    ):
        return [
            exp
            for exp in self.experiences
            if exp.strategy == strategy
        ]

    def find_similar(
        self,
        strategy: str,
        success: bool | None = None
    ):
        results = []

        for exp in self.experiences:

            if exp.strategy != strategy:
                continue

            if success is not None:
                if exp.success != success:
                    continue

            results.append(exp)

        return results