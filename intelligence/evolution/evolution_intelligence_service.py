from intelligence.evolution.evolution_report import (
    EvolutionReport
)


class EvolutionIntelligenceService:


    def __init__(
        self,
        analytics,
        history,
        explainer=None
    ):

        self.analytics = analytics

        self.history = history

        self.explainer = explainer



    def analyze(self):

        records = self.history.all()


        if not records:

            return EvolutionReport(

                total_evolutions=0,

                best_strategy=None,

                average_improvement=0,

                strongest_rank="UNKNOWN",

                success_rate=0,

                explanation=None

            )


        best = self.analytics.best_child()


        average = (
            self.analytics.average_improvement()
        )


        successes = [

            r for r in records

            if r.score_after > r.score_before

        ]


        success_rate = (
            len(successes)
            /
            len(records)
            *
            100
        )


        rank = "STABLE"


        if average >= 10:

            rank = "EXCELLENT"

        elif average >= 5:

            rank = "GOOD"



        explanation = None


        if self.explainer:

            latest = records[-1]

            explanation = (
                self.explainer.explain(
                    latest
                )
            )



        return EvolutionReport(

            total_evolutions=len(records),

            best_strategy=best.child,

            average_improvement=average,

            strongest_rank=rank,

            success_rate=success_rate,

            explanation=explanation

        )