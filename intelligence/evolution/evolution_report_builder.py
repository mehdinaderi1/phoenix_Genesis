class EvolutionReportBuilder:


    def __init__(
        self,
        analytics,
        ranker,
        explainer
    ):

        self.analytics = analytics
        self.ranker = ranker
        self.explainer = explainer



    def build(self):

        history = self.analytics.history.all()


        if not history:

            return {

                "summary": {
                    "total_evolutions": 0,
                    "best_strategy": None,
                },

                "ranking": {
                    "rank": "UNKNOWN",
                    "score": 0,
                },

                "explanation": None
            }



        best = self.analytics.best_child()


        ranking = self.ranker.rank(
            history
        )


        explanation = self.explainer.explain(
            best
        )


        return {

            "summary": {

                "total_evolutions":
                    self.analytics.count(),

                "best_strategy":
                    best.child,

                "average_improvement":
                    self.analytics.average_improvement()

            },


            "ranking": ranking,


            "explanation": explanation

        }