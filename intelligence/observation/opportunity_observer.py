"""Read-only observer for recording market opportunities and decision gates."""

from copy import deepcopy
from datetime import datetime, timezone

from intelligence.decision_rules import DecisionRules


class OpportunityObserver:
    """Describe opportunities without placing or modifying orders."""

    def __init__(self, decision_rules=None, clock=None):
        self.decision_rules = decision_rules or DecisionRules()
        self.clock = clock or (
            lambda: datetime.now(timezone.utc).isoformat()
        )

    @staticmethod
    def _filter(passed, reason):
        return {"passed": bool(passed), "reason": reason}

    def _filters(self, report):
        signal = getattr(report, "signal", None)
        is_buy = signal == "BUY"
        is_sell = signal == "SELL"
        directional = is_buy or is_sell

        strategy_passed = self.decision_rules.strategy_is_valid(report)
        consensus_passed = self.decision_rules.consensus_is_valid(report)

        if is_buy:
            risk_passed = getattr(report, "risk", None) == "LOW"
            threshold = 80
            confidence_passed = getattr(report, "confidence", 0) >= threshold
        elif is_sell:
            # Current SHORT rules do not require LOW risk.
            risk_passed = True
            threshold = 70
            confidence_passed = getattr(report, "confidence", 0) >= threshold
        else:
            risk_passed = False
            threshold = None
            confidence_passed = False

        consensus = getattr(report, "strategy_consensus", None)
        operational = getattr(report, "operational_strategy_result", None)

        if operational is None:
            operational_passed = True
            operational_reason = (
                "No operational strategy gate supplied; no additional gate applied."
            )
        else:
            operational_passed = bool(operational.get("matched", False)) and (
                (is_buy and operational.get("signal") == "BUY")
                or (is_sell and operational.get("signal") == "SELL")
            )
            operational_reason = (
                "Operational strategy matches the candidate direction."
                if operational_passed
                else "Operational strategy did not match the candidate direction."
            )

        return {
            "strategy": self._filter(
                strategy_passed,
                "Champion strategy passed current rules."
                if strategy_passed
                else "Champion strategy is missing ACTIVE status.",
            ),
            "consensus": self._filter(
                consensus_passed,
                (
                    "Strategy consensus passed current rules."
                    if consensus_passed and consensus is not None
                    else "No consensus supplied; current rules allow this gate."
                    if consensus_passed
                    else "Consensus failed: check decision, signal alignment, support, and confidence."
                ),
            ),
            "signal": self._filter(
                directional,
                "Directional BUY/SELL signal present."
                if directional
                else f"Signal {signal!r} is not a directional candidate.",
            ),
            "risk": self._filter(
                risk_passed,
                (
                    "Risk is LOW, as required for LONG."
                    if is_buy and risk_passed
                    else "LONG requires risk == LOW under current rules."
                    if is_buy
                    else "Current SHORT rules do not require LOW risk; risk recorded for visibility."
                    if is_sell
                    else "No directional candidate; side-specific risk gate is not applicable."
                ),
            ),
            "confidence": self._filter(
                confidence_passed,
                (
                    f"Confidence meets the current {threshold} threshold."
                    if confidence_passed and threshold is not None
                    else f"Confidence is below the current {threshold} threshold."
                    if threshold is not None
                    else "No directional candidate; side-specific confidence gate is not applicable."
                ),
            ),
            "operational_strategy": self._filter(
                operational_passed, operational_reason
            ),
        }

    def observe(
        self,
        report,
        decision=None,
        reference_price=None,
        symbol=None,
        observation_timestamp=None,
    ):

        """Return an observation record for an already-made decision."""
        if decision is None:
            raise ValueError(
                "decision is required; OpportunityObserver must not decide or execute."
            )

        filters = self._filters(report)
        blocked_reasons = [
            f"{name}: {details['reason']}"
            for name, details in filters.items()
            if not details["passed"]
        ]

        trace = getattr(decision, "trace", None)
        if not isinstance(trace, dict):
            metadata = getattr(decision, "metadata", {}) or {}
            trace = metadata.get("trace", {})

        return {
            "observed_at": self.clock(),
            "observation_timestamp": observation_timestamp,
            "symbol": getattr(report, "symbol", None) or symbol,
            "timeframe": getattr(report, "timeframe", None),
            "trend": getattr(report, "trend", None),
            "regime": getattr(report, "regime", None),
            "signal": getattr(report, "signal", None),
            "confidence": getattr(report, "confidence", None),
            "risk": getattr(report, "risk", None),
            "reference_price": (
                getattr(report, "reference_price", None)
                if getattr(report, "reference_price", None) is not None
                else reference_price
            ),
            "signal_timestamp": getattr(report, "signal_timestamp", None),
            "decision": getattr(decision, "action", "UNKNOWN"),
            "filters": filters,
            "blocked_reasons": blocked_reasons,
            "decision_trace": deepcopy(trace) if trace else {},
            "execution_attempted": False,
        }
