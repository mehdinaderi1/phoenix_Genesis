from intelligence.market_report import MarketReport


class ReportBuilder:

    def build(self, symbol, reasoning_output, risk_level="Unknown", confidence=0):

        return MarketReport(
            symbol=symbol,

            trend=reasoning_output.get(
                "trend",
                "Unknown"
            ),

            momentum=reasoning_output.get(
                "momentum",
                "Unknown"
            ),

            regime=reasoning_output.get(
                "regime",
                "Unknown"
            ),

            risk_level=risk_level,

            confidence=confidence,

            reasoning=reasoning_output.get(
                "reasoning",
                "No reasoning available."
            )
        )