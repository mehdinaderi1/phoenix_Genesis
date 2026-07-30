from intelligence.governance.governance_analyzer import (
    GovernanceAnalyzer
)

from intelligence.governance.governance_learning import (
    GovernanceLearning
)


class GovernanceService:


    def __init__(
        self,
        history,
        analyzer=None,
        learning=None
    ):

        self.history = history


        self.analyzer = (
            analyzer
            or GovernanceAnalyzer()
        )


        self.learning = (
            learning
            or GovernanceLearning()
        )



    def evaluate(
        self,
        strategy
    ):


        records = []


        if self.history:

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


        learning_result = (
            self.learning.analyze_history()
        )


        return {
            "strategy": strategy,
            "status": result["status"],
            "confidence": result["score"],
            "learning": learning_result
        }