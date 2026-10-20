import os
from collections import Counter

from intelligence.consensus import ConsensusResult


class MultiTimeframeAnalyzer:
    """
    Multi-timeframe consensus analyzer.

    Two modes:
    - Legacy (default): any signal conflict -> WAIT, 50% penalty
    - New: dominance-based penalty, dominant signal wins

    Activated via PHOENIX_SMART_CONFLICT=1
    """

    USE_SMART_CONFLICT = (
        os.getenv("PHOENIX_SMART_CONFLICT", "0").strip() == "1"
    )

    def get_weight(self, timeframe):
        weights = {
            "30m": 1,
            "4H": 2,
            "1D": 3,
            "Daily": 3,
        }
        return weights.get(timeframe, 1)

    def _legacy_conflict(self, signals):
        """Legacy behavior: strict conflict detection."""
        signal_conflict = len(set(signals)) != 1
        conflict_penalty = 0.5 if signal_conflict else 1.0

        if signal_conflict:
            return "WAIT", conflict_penalty, True, "SIGNAL_CONFLICT"

        return signals[0], 1.0, False, None

    def _smart_conflict(self, signals):
        """
        Dominance-based conflict resolution.

        - If one signal dominates (>=60%), use it with small penalty.
        - If moderate dominance (>=40%), use it with medium penalty.
        - Otherwise, WAIT with heavy penalty.
        """
        if not signals:
            return "WAIT", 0.5, True, "SIGNAL_CONFLICT"

        counts = Counter(signals)
        dominant, dom_count = counts.most_common(1)[0]
        dominance = dom_count / len(signals)

        if dominance >= 0.6:
            return dominant, 0.85, False, None
        elif dominance >= 0.4:
            return dominant, 0.7, True, None
        else:
            return "WAIT", 0.5, True, "SIGNAL_CONFLICT"

    def analyze(self, analyses):
        if not analyses:
            return ConsensusResult(
                trend="UNKNOWN",
                signal="WAIT",
                confidence=0,
                reason_code="SIGNAL_INSUFFICIENT_DATA",
            )

        signals = [item.signal for item in analyses]
        weighted_sum = 0
        total_weight = 0
        timeframe_breakdown = []

        for item in analyses:
            weight = self.get_weight(item.timeframe)

            weighted_sum += item.confidence * weight
            total_weight += weight

            timeframe_breakdown.append({
                "timeframe": item.timeframe,
                "confidence": item.confidence,
                "weight": weight,
                "signal": item.signal,
                "trend": item.trend,
                "reasons": list(getattr(item, "reasons", ())),
            })

        average_confidence = weighted_sum / total_weight

        # انتخاب منطق بر اساس flag
        if self.USE_SMART_CONFLICT:
            final_signal, conflict_penalty, signal_conflict, reason_code = (
                self._smart_conflict(signals)
            )
        else:
            final_signal, conflict_penalty, signal_conflict, reason_code = (
                self._legacy_conflict(signals)
            )

        final_confidence = average_confidence * conflict_penalty

        trends = [item.trend for item in analyses]
        final_trend = max(set(trends), key=trends.count)

        breakdown = {
            "timeframes": timeframe_breakdown,
            "weighted_confidence": average_confidence,
            "signal_conflict": signal_conflict,
            "conflict_penalty": conflict_penalty,
            "final_confidence": final_confidence,
        }

        return ConsensusResult(
            trend=final_trend,
            signal=final_signal,
            confidence=final_confidence,
            breakdown=breakdown,
            reason_code=reason_code,
        )