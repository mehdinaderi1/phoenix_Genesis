class BTCMTFTrendAlignmentV1:
    name = "BTC_MTF_TREND_ALIGNMENT_V1"
    symbol = "BTCUSDT"
    market = "FUTURES"
    primary_timeframe = "5m"
    context_timeframes = ["15m", "30m"]
    higher_timeframe = "4H"

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

    def evaluate(self, timeframe_states):
        primary_signal = timeframe_states.get("5m")

        if primary_signal == "BUY":
            aligned = all(
                timeframe_states.get(timeframe) == expected
                for timeframe, expected in self.long_conditions.items()
            )
            return {
                "signal": "BUY",
                "direction": "LONG",
                "matched": aligned,
            }

        if primary_signal == "SELL":
            aligned = all(
                timeframe_states.get(timeframe) == expected
                for timeframe, expected in self.short_conditions.items()
            )
            return {
                "signal": "SELL",
                "direction": "SHORT",
                "matched": aligned,
            }

        return {
            "signal": "WAIT",
            "direction": None,
            "matched": False,
        }
