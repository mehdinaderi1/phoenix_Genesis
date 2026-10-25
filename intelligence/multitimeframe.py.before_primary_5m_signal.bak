from intelligence.consensus import ConsensusResult


class MultiTimeframeAnalyzer:

    def get_weight(self, timeframe):
        weights = {
            "30m": 1,
            "4H": 2,
            "1D": 3,
            "Daily": 3
        }
        return weights.get(timeframe, 1)

    def analyze(self, analyses):
        if not analyses:
            return ConsensusResult(
                trend="UNKNOWN",
                signal="WAIT",
                confidence=0
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
                "reasons": list(getattr(item, "reasons", ()))
            })

        average_confidence = weighted_sum / total_weight
        signal_conflict = len(set(signals)) != 1
        conflict_penalty = 0.5 if signal_conflict else 1.0

        if signal_conflict:
            final_signal = "WAIT"
            final_confidence = average_confidence * conflict_penalty
        else:
            final_signal = signals[0]
            final_confidence = average_confidence

        trends = [item.trend for item in analyses]
        final_trend = max(set(trends), key=trends.count)

        breakdown = {
            "timeframes": timeframe_breakdown,
            "weighted_confidence": average_confidence,
            "signal_conflict": signal_conflict,
            "conflict_penalty": conflict_penalty,
            "final_confidence": final_confidence
        }

        return ConsensusResult(
            trend=final_trend,
            signal=final_signal,
            confidence=final_confidence,
            breakdown=breakdown
        )
