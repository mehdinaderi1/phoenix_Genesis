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

        # 2. decision.strategy
        strategy = getattr(decision, "strategy", None)
        name = self._extract_strategy_name(strategy)
        if name:
            return name

        # 3. metadata.champion_strategy
        metadata = getattr(decision, "metadata", {}) or {}

        # 3.5. metadata.operational_strategy  ← NEW
        operational = metadata.get("operational_strategy")
        if isinstance(operational, dict):
            op_name = operational.get("strategy") or operational.get("name")
            if op_name:
                return op_name

        champion_meta = metadata.get("champion_strategy")
        name = self._extract_strategy_name(champion_meta)
        if name:
            return name

        # 4. Fallback
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
        pnl=None,
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
            # ✱ اگر PnL واقعی داده شده، از آن استفاده کن.
            #    وگرنه fallback به اختلاف قیمت (برای سازگاری).
            actual_pnl = (
                pnl if pnl is not None
                else (exit_price - entry_price)
            )

            performance = PerformanceRecord(
                strategy=resolved_strategy,
                profit_loss=actual_pnl,        # ✱ CHANGED
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