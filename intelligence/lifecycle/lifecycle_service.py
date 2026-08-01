from intelligence.lifecycle.lifecycle_metrics_engine import (
    LifecycleMetricsEngine
)

from intelligence.lifecycle.lifecycle_decision import (
    LifecycleDecisionEngine
)


class LifecycleService:
    def __init__(self):
        self.metrics_engine = LifecycleMetricsEngine()
        self.decision_engine = LifecycleDecisionEngine()

    def evaluate(self, history):
        metrics = self.metrics_engine.calculate(history)
        decision = self.decision_engine.decide(metrics)

        return {
            "metrics": metrics,
            "decision": decision
        }