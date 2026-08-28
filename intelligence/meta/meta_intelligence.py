from intelligence.meta.decision_performance_analyzer import (
    DecisionPerformanceAnalyzer
)

from intelligence.meta.meta_bias_analyzer import (
    MetaBiasAnalyzer
)

from intelligence.meta.meta_insight import MetaInsight

from intelligence.meta.meta_feedback_analyzer import (
    MetaFeedbackAnalyzer
)


class MetaIntelligence:


    def __init__(self):

        self.performance_analyzer = (
            DecisionPerformanceAnalyzer()
        )

        self.bias_analyzer = (
            MetaBiasAnalyzer()
        )

        self.meta_feedback_analyzer = (
            MetaFeedbackAnalyzer()
        )


    def analyze(
        self,
        decision_records,
        meta_feedback_records=None
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

        if meta_feedback_records:

            insight.meta_feedback = (
                self.meta_feedback_analyzer.analyze(
                    meta_feedback_records
                )
            )


        return insight