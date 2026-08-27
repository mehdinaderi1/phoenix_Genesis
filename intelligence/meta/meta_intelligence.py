from intelligence.meta.decision_performance_analyzer import (
    DecisionPerformanceAnalyzer
)

from intelligence.meta.meta_bias_analyzer import (
    MetaBiasAnalyzer
)

from intelligence.meta.meta_insight import MetaInsight


class MetaIntelligence:


    def __init__(self):

        self.performance_analyzer = (
            DecisionPerformanceAnalyzer()
        )

        self.bias_analyzer = (
            MetaBiasAnalyzer()
        )


    def analyze(
        self,
        decision_records
    ):

        insight = (
            self.performance_analyzer.analyze(
                decision_records
            )
        )


        bias = (
            self.bias_analyzer.detect(
                insight
            )
        )


        insight.bias = bias


        return insight