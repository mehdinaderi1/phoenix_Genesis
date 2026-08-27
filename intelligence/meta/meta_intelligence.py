from intelligence.meta.decision_performance_analyzer import (
    DecisionPerformanceAnalyzer
)


class MetaIntelligence:


    def __init__(self):

        self.performance_analyzer = (
            DecisionPerformanceAnalyzer()
        )


    def analyze(
        self,
        decision_records
    ):

        return (
            self.performance_analyzer.analyze(
                decision_records
            )
        )