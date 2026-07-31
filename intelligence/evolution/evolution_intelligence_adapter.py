class EvolutionIntelligenceAdapter:


    def __init__(
        self,
        selector
    ):

        self.selector = selector



    def analyze(
        self,
        lineages
    ):

        result = self.selector.select(
            lineages
        )


        if not result:

            return {

                "available": False,

                "strategy": None

            }


        return {

            "available": True,

            "strategy": result["lineage"],

            "analysis": result["analysis"]

        }