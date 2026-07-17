from collections import defaultdict


class ExperienceAnalyzer:
    """
    Analyze Phoenix experiences
    and extract successful patterns.
    """

    def __init__(self, experience_memory):
        self.experience_memory = experience_memory


    def analyze(self):

        experiences = (
            self.experience_memory.get_experiences()
        )

        patterns = defaultdict(list)

        for exp in experiences:

            key = (
                exp.regime,
                exp.signal,
                exp.risk
            )

            patterns[key].append(exp)

        return self._build_patterns(patterns)


    def _build_patterns(self, grouped):

        results = []

        for key, items in grouped.items():

            total = len(items)

            successes = [
                exp
                for exp in items
                if exp.success
            ]

            success_rate = (
                len(successes) / total
                if total
                else 0
            )

            avg_score = (
                sum(exp.score for exp in items)
                / total
                if total
                else 0
            )

            results.append(
                {
                    "pattern": key,
                    "samples": total,
                    "success_rate": round(
                        success_rate,
                        2
                    ),
                    "avg_score": round(
                        avg_score,
                        2
                    )
                }
            )

        return results