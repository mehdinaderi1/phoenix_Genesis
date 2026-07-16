from collections import defaultdict

from intelligence.learning.experience_record import ExperienceRecord


class PatternDetector:

    def analyze(
        self,
        experiences: list[ExperienceRecord],
    ) -> dict:

        patterns = defaultdict(
            lambda: {
                "total": 0,
                "success": 0,
            }
        )

        for experience in experiences:

            key = (
                experience.strategy,
                experience.regime,
            )

            patterns[key]["total"] += 1

            if experience.outcome == "SUCCESS":
                patterns[key]["success"] += 1

        results = {}

        for key, value in patterns.items():

            win_rate = (
                value["success"]
                /
                value["total"]
                *
                100
            )

            results[key] = {
                "trades": value["total"],
                "win_rate": win_rate,
            }

        return results