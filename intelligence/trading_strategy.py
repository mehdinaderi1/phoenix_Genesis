import os


class BTCMTFTrendAlignmentV1:
    name = "BTC_MTF_TREND_ALIGNMENT_V1"
    symbol = "BTCUSDT"
    market = "FUTURES"
    primary_timeframe = "5m"
    context_timeframes = ["15m", "30m", "1H"]
    higher_timeframe = "4H"

    USE_RELAXED_ALIGNMENT = (
        os.getenv("PHOENIX_RELAXED_ALIGNMENT", "0").strip() == "1"
    )

    USE_VETO_ALIGNMENT = (
        os.getenv("PHOENIX_VETO_ALIGNMENT", "0").strip() == "1"
    )

    long_conditions = {
        "4H": "BULLISH",
        "30m": "BULLISH",
        "15m": "BULLISH",
        "5m": "BUY",
    }

    short_conditions = {
        "4H": "BEARISH",
        "30m": "BEARISH",
        "15m": "BEARISH",
        "5m": "SELL",
    }

    def to_memory_record(self):
        return {
            "strategy": self.name,
            "regime": None,
            "signal": None,
            "risk": None,
            "status": "CANDIDATE",
            "samples": 0,
            "success_rate": 0,
            "score": 0,
        }

    def states_from_breakdown(self, breakdown):
        if breakdown is None:
            return {}
        return {
            item["timeframe"]: (
                item["signal"]
                if item["timeframe"] == "5m"
                else item["trend"]
            )
            for item in breakdown["timeframes"]
        }

    def _count_matches(self, states, conditions):
        matched = 0.0
        total = 0
        for tf, expected in conditions.items():
            total += 1
            actual = states.get(tf)
            if actual == expected:
                matched += 1
            elif expected == "BULLISH" and actual == "BUY":
                matched += 0.5
            elif expected == "BEARISH" and actual == "SELL":
                matched += 0.5
        return matched, total

    def evaluate(self, timeframe_states):
        # ─── env را در زمان فراخوانی بخوان، نه import ───
        use_relaxed = (
            os.getenv("PHOENIX_RELAXED_ALIGNMENT", "0").strip() == "1"
        )
        use_veto = (
            os.getenv("PHOENIX_VETO_ALIGNMENT", "0").strip() == "1"
        )
        # ─────────────────────────────────────────────────

        if not timeframe_states:
            return {
                "signal": "WAIT",
                "direction": None,
                "matched": False,
            }

        if use_veto:
            trend_1d = timeframe_states.get("1D")
            if trend_1d == "BEARISH":
                long_score = 0.0
            else:
                long_score, _ = self._count_matches(
                    timeframe_states, self.long_conditions
                )
            if trend_1d == "BULLISH":
                short_score = 0.0
            else:
                short_score, _ = self._count_matches(
                    timeframe_states, self.short_conditions
                )
        else:
            long_score, _ = self._count_matches(
                timeframe_states, self.long_conditions
            )
            short_score, _ = self._count_matches(
                timeframe_states, self.short_conditions
            )

        threshold = 2.5 if use_relaxed else 4.0

        if long_score >= threshold and long_score > short_score:
            return {
                "signal": "BUY",
                "direction": "LONG",
                "matched": True,
            }

        if short_score >= threshold and short_score > long_score:
            return {
                "signal": "SELL",
                "direction": "SHORT",
                "matched": True,
            }

        return {
            "signal": "WAIT",
            "direction": None,
            "matched": False,
        }