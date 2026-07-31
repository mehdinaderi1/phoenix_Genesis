class EvolutionIntelligence:


    def __init__(
        self,
        analyzer
    ):

        self.analyzer = analyzer



    def evaluate(
        self,
        strategy_name
    ):

        analysis = self.analyzer.analyze(
            strategy_name
        )


        recommendation = (
            analysis["recommendation"]
        )


        if recommendation == "EVOLVE":

            decision = "ALLOW"


        elif recommendation == "CAUTION":

            decision = "REVIEW"


        else:

            decision = "NEW"



        return {

            "decision": decision,

            "analysis": analysis

        }