import os
from intelligence.decision import DecisionResult
from intelligence.decision_rules import DecisionRules
from intelligence.decision_trace import DecisionTrace
from intelligence.strategy_consensus_explanation_builder import (
    StrategyConsensusExplanationBuilder
)
from intelligence.trend_filter import passes_trend_filter


class DecisionEngine:

    def __init__(self):
        self.rules = DecisionRules()
        self.explanation_builder = StrategyConsensusExplanationBuilder()

    def _consensus_metadata(self, report):
        consensus = getattr(report, "strategy_consensus", None)
        if not consensus:
            return {}
        return {
            "consensus_confidence":   consensus.get("confidence", 0.0),
            "supporting_strategies":  consensus.get("supporting_strategies", 0),
            "opposing_strategies":    consensus.get("opposing_strategies", 0),
            "top_strategy":           consensus.get("top_strategy"),
        }

    def _build_trace(self, report, action, explanation, trend=None):
        trend = trend or {"long": True, "short": True}
        trace = DecisionTrace(
            decision=action,
            signal=getattr(report, "signal", None),
            confidence=report.confidence,
            risk=getattr(report, "risk", "UNKNOWN"),
            strategy_consensus=getattr(report, "strategy_consensus", {}),
            gates={
                "strategy":   self.rules.strategy_is_valid(report),
                "consensus":  self.rules.consensus_is_valid(report),
                "signal":     getattr(report, "signal", None) in ["BUY", "SELL"],
                "risk":       getattr(report, "risk", None) == "LOW",
                "confidence": getattr(report, "confidence", 0) >= float(
                os.environ.get("PHOENIX_CONFIDENCE_GATE", "80")
            ),
                "trend_long":  trend["long"],
                "trend_short": trend["short"],
            },
            explanation=explanation,
        )
        return trace.to_dict()

    def _build_explanation(self, report):
        consensus = getattr(report, "strategy_consensus", None)
        if not consensus:
            return {}
        return self.explanation_builder.build(consensus).to_dict()

    def decide(self, report):

        metadata = self._consensus_metadata(report)
        metadata["champion_strategy"] = getattr(report, "champion_strategy", None)

        explanation = self._build_explanation(report)

        operational_strategy = getattr(report, "operational_strategy_result", None)
        strategy_allows_long = True
        strategy_allows_short = True

        if operational_strategy is not None:
            matched = operational_strategy.get("matched", False)
            strategy_signal = operational_strategy.get("signal")

            if not matched:
                strategy_allows_long = False
                strategy_allows_short = False
            else:
                strategy_allows_long = strategy_signal == "BUY"
                strategy_allows_short = strategy_signal == "SELL"

        # ─── Bypass: اگر consensus قوی است، استراتژی را دور بزن ───
        _cs = getattr(report, "signal", None)
        _cc = getattr(report, "confidence", 0)
        _min_action_conf = float(os.environ.get(
            "PHOENIX_MIN_ACTION_CONFIDENCE", "50"
        ))
        if _cs in ("BUY", "SELL") and _cc >= _min_action_conf:
            if _cs == "BUY":
                strategy_allows_long = True
            elif _cs == "SELL":
                strategy_allows_short = True
        # ─────────────────────────────────────────────────────────     
       
        # ─── Trend filter (EMA) — همیشه محاسبه شود ───
        candles = (
            getattr(report, "candles", None)
            or getattr(report, "candles_df", None)
            or getattr(report, "ohlcv", None)
        )
        trend_long, trend_short = passes_trend_filter(candles)
        trend = {"long": trend_long, "short": trend_short}
        # ──────────────────────────────────────────────

        can_long = (
            strategy_allows_long
            and trend_long
            and self.rules.can_long(report)
        )
        can_short = (
            strategy_allows_short
            and trend_short
            and self.rules.can_short(report)
        )

        print("CAN SHORT:", can_short)
        print("SHORT CHECK:", {
            "strategy_valid":  self.rules.strategy_is_valid(report),
            "consensus_valid": self.rules.consensus_is_valid(report),
            "signal":          report.signal,
            "risk":            report.risk,
            "confidence":      report.confidence,
            "trend_short":     trend_short,
        })
        print("CAN LONG:", can_long)
        print("LONG CHECK:", {
            "strategy_valid":  self.rules.strategy_is_valid(report),
            "consensus_valid": self.rules.consensus_is_valid(report),
            "signal":          report.signal,
            "risk":            report.risk,
            "confidence":      report.confidence,
            "trend_long":      trend_long,
        })

        if can_long:
            trace = self._build_trace(report, "PREPARE_LONG", explanation, trend)
            return DecisionResult(
                action="PREPARE_LONG",
                reason="Strong bullish signal with strategy consensus",
                confidence=report.confidence,
                regime=getattr(report, "regime", None),
                signal=getattr(report, "signal", None),
                risk=getattr(report, "risk", None),
                trace=trace,
                explanation=explanation,
                metadata={**metadata, "trace": trace},
                **metadata
            )

        elif can_short:
            trace = self._build_trace(report, "PREPARE_SHORT", explanation, trend)
            return DecisionResult(
                action="PREPARE_SHORT",
                reason="Bearish market conditions with strategy consensus",
                confidence=report.confidence,
                regime=getattr(report, "regime", None),
                signal=getattr(report, "signal", None),
                risk=getattr(report, "risk", None),
                trace=trace,
                explanation=explanation,
                metadata={**metadata, "trace": trace},
                **metadata
            )

        else:
            long_ok, long_reason = self.rules.diagnose_long(report)
            short_ok, short_reason = self.rules.diagnose_short(report)

            if strategy_allows_short:
                reason_code = short_reason or "UNKNOWN"
            elif strategy_allows_long:
                reason_code = long_reason or "UNKNOWN"
            else:
                reason_code = "STRATEGY_NOT_MATCHED"

            trace = self._build_trace(report, "WAIT", explanation, trend)
            return DecisionResult(
                action="WAIT",
                reason="Market conditions require monitoring",
                confidence=report.confidence,
                regime=getattr(report, "regime", None),
                signal=getattr(report, "signal", None),
                risk=getattr(report, "risk", None),
                trace=trace,
                explanation=explanation,
                metadata={**metadata, "trace": trace},
                reason_code=reason_code,
                **metadata
            )