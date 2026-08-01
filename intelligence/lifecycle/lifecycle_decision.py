from dataclasses import dataclass



@dataclass
class LifecycleDecision:

    action: str

    reason: str

    score: float



class LifecycleDecisionEngine:


    def decide(
        self,
        metrics
    ):

        score = metrics.lifecycle_score

        state = metrics.current_state



        # Champion strategy with strong lifecycle
        if (
            state == "CHAMPION"
            and score >= 80
        ):

            return LifecycleDecision(

                action="KEEP",

                reason="champion strategy is healthy",

                score=score

            )



        # Active strategy needs improvement
        if (
            state == "ACTIVE"
            and score < 50
        ):

            return LifecycleDecision(

                action="IMPROVE",

                reason="active strategy needs improvement",

                score=score

            )



        # Retired strategies should be archived

        if state == "RETIRED":

            return LifecycleDecision(

                action="ARCHIVE",

                reason="retired strategy lifecycle completed",

                score=score

            )



        # Candidate strategies continue evaluation

        if state == "CANDIDATE":

            return LifecycleDecision(

                action="EVALUATE",

                reason="candidate strategy requires validation",

                score=score

            )



        return LifecycleDecision(

            action="MONITOR",

            reason="strategy lifecycle requires monitoring",

            score=score

        )