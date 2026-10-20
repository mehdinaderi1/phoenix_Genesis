from intelligence.outcome_record import OutcomeRecord
from intelligence.performance_record import PerformanceRecord


class DecisionOutcomeBridge:

    def __init__(
        self,
        outcome_memory,
        performance_feedback,
        strategy_performance_memory,
        performance_learning=None,
    ):
        self.outcome_memory = outcome_memory
        self.performance_feedback = performance_feedback
        self.strategy_performance_memory = strategy_performance_memory
        self.performance_learning = performance_learning

    @staticmethod
    def _extract_strategy_name(value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get("name")
        if isinstance(value, str):
            return value
        name = getattr(value, "name", None)
        if name is not None:
            return name
        return None

    def _resolve_strategy(self, decision):
        # 1. champion_strategy
        champion = getattr(decision, "champion_strategy", None)
        name = self._extract_strategy_name(champion)
        if name:
            return name

        # 2. decision.strategy (may be dict or str)
        strategy = getattr(decision, "strategy", None)
        name = self._extract_strategy_name(strategy)
        if name:
            return name

        # 3. metadata.champion_strategy
        metadata = getattr(decision, "metadata", {}) or {}
        champion = metadata.get("champion_strategy")
        name = self._extract_strategy_name(champion)
        if name:
            return name

        # 4. Fallback: regime_signal_risk
        regime = getattr(decision, "regime", None)
        signal = getattr(decision, "signal", None)
        risk = getattr(decision, "risk", None)
        if regime or signal or risk:
            return f"{regime}_{signal}_{risk}"

        return None

    def process(
        self,
        decision,
        entry_price,
        exit_price,
        strategy=None,
    ):
        outcome = OutcomeRecord(
            decision=decision,
            entry_price=entry_price,
            exit_price=exit_price,
        )

        self.outcome_memory.save_outcome(outcome)

        feedback = self.performance_feedback.evaluate(outcome)

        resolved_strategy = (
            strategy
            if strategy is not None
            else self._resolve_strategy(decision)
        )

        performance = None
        performance_learning = None

        if resolved_strategy:
            performance = PerformanceRecord(
                strategy=resolved_strategy,
                profit_loss=(exit_price - entry_price),
                success=(feedback["result"] == "SUCCESS"),
            )

            self.strategy_performance_memory.save_performance(performance)

            if self.performance_learning:
                performance_learning = self.performance_learning.process(
                    performance,
                    decision,
                )

        return {
            "result": feedback["result"],
            "score": feedback["score"],
            "feedback": feedback,
            "performance": performance,
            "performance_learning": performance_learning,
        }