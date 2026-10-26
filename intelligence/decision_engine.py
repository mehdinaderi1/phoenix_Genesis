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
        signal = getattr(report, "signal", None)
        risk = getattr(report, "risk", None)

        # Risk gate must match the direction we are evaluating
        if signal == "SELL":
            risk_allowed = risk in self.rules.SHORT_ALLOWED_RISK
        else:
            risk_allowed = risk in self.rules.LONG_ALLOWED_RISK

        trace = DecisionTrace(
            decision=action,
            signal=signal,
            confidence=report.confidence,
            risk=getattr(report, "risk", "UNKNOWN"),
            strategy_consensus=getattr(report, "strategy_consensus", {}),
            gates={
                "strategy":   self.rules.strategy_is_valid(report),
                "consensus":  self.rules.consensus_is_valid(report),
                "signal":     signal in ["BUY", "SELL"],
                "risk":       risk_allowed,
                "confidence": getattr(report, "confidence", 0) >= float(
                    os.environ.get("PHOENIX_CONFIDENCE_GATE", "80")
                ),
                "trend_long":  trend["long"],
                "trend_short": trend["short"],
            },
            explanation=explanation,
        )
        return trace.to_dict()

    def _compute_volatility(self, candles):
        """Compute ATR-based volatility percentage from candles.

        Caller must supply fresh candles (decide() handles the fetch).
        Returns None if not computable.
        """
        if not candles or len(candles) < 15:
            return None

        def _ohlc(c):
            """Return (high, low, close) from candle (dict, object, or list [ts,o,h,l,c,v])."""
            if isinstance(c, (list, tuple)) and len(c) >= 5:
                return float(c[2]), float(c[3]), float(c[4])
            if isinstance(c, dict):
                return c.get("high"), c.get("low"), c.get("close")
            if hasattr(c, "high"):
                return c.high, c.low, getattr(c, "close", None)
            return None, None, None

        trs = []
        for i in range(1, len(candles)):
            h, l, _ = _ohlc(candles[i])
            _, _, pc_close = _ohlc(candles[i - 1])

            if h is None or l is None or pc_close is None:
                continue
            trs.append(max(h - l, abs(h - pc_close), abs(l - pc_close)))

        if len(trs) < 14:
            return None

        atr = sum(trs[-14:]) / 14
        _, _, last_close = _ohlc(candles[-1])

        if not last_close or last_close <= 0:
            return None

        return atr / last_close * 100

    def _build_explanation(self, report):
        consensus = getattr(report, "strategy_consensus", None)
        if not consensus:
            return {}
        return self.explanation_builder.build(consensus).to_dict()

    def _fetch_fresh_candles(self, report):
        """Return fresh 30m candles; fall back to report.candles if XT fails."""
        candles = (
            getattr(report, "candles", None)
            or getattr(report, "candles_df", None)
            or getattr(report, "ohlcv", None)
        )
        try:
            from exchanges.xt_exchange import XTExchange
            _ex = XTExchange(timeout=10)
            fresh = _ex.get_historical_candles("BTCUSDT", "30m", limit=250)
            if fresh and len(fresh) >= 15:
                candles = fresh
        except Exception:
            pass
        return candles

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

        # ─── Fresh candles (shared by TREND + VOLGATE) ───
        candles = self._fetch_fresh_candles(report)

        # ─── Trend filter (EMA) — همیشه محاسبه شود ───
        trend_long, trend_short = passes_trend_filter(candles)
        if os.environ.get("DISABLE_TREND_FILTER", "0").strip() == "1":
            trend_long, trend_short = True, True
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

        # Volatility gate (env-configurable, default OFF)
        _min_vol = float(os.getenv("PHOENIX_MIN_VOLATILITY_PCT", "0") or 0)
        print(f"[VOLGATE] enabled={'yes' if _min_vol > 0 else 'no'} min_vol={_min_vol}")
        if _min_vol > 0:
            _vol_pct = self._compute_volatility(candles)
            report.volatility_pct = _vol_pct
            print(f"[VOLGATE] vol_pct={_vol_pct} threshold={_min_vol} regime={getattr(report,'regime','?')}")

            if _vol_pct is not None and _vol_pct < _min_vol:
                trace = self._build_trace(report, "WAIT", explanation, trend)
                return DecisionResult(
                    action="WAIT",
                    reason=f"LOW_VOLATILITY ({_vol_pct:.3f}% < {_min_vol}%)",
                    confidence=report.confidence,
                    regime=getattr(report, "regime", None),
                    signal=getattr(report, "signal", None),
                    risk=getattr(report, "risk", None),
                    trace=trace,
                    explanation=explanation,
                    metadata={**metadata, "trace": trace},
                    reason_code="LOW_VOLATILITY",
                    **metadata,
                )

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