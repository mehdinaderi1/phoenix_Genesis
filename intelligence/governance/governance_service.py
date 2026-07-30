from intelligence.governance.governance_analyzer import (
    GovernanceAnalyzer
)


class GovernanceService:


    def __init__(
        self,
        history,
        analyzer=None
    ):

        self.history = history

        self.analyzer = (
            analyzer
            or GovernanceAnalyzer()
        )



    def evaluate(
        self,
        strategy
    ):


        records = []


        for item in self.history.get_all():

            if (
                item.get("strategy")
                == strategy
            ):

                records.append(
                    item
                )



        result = self.analyzer.analyze(
            records
        )


        return {
            "strategy": strategy,
            "status": result["status"],
            "confidence": result["score"]
        }