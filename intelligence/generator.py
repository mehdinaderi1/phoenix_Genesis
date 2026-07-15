from intelligence.report import MarketReport


class ReportGenerator:

    def generate(self, report: MarketReport):

        return f"""
🦅 PHOENIX MARKET REPORT

Symbol:
{report.symbol}

Timeframe:
{report.timeframe}

Trend:
{report.trend}

Signal:
{report.signal}

Confidence:
{report.confidence}%

Risk:
{report.risk}

Reasons:
{self._format_reasons(report.reasons)}
"""

    def _format_reasons(self, reasons):

        return "\n".join(
            f"- {reason}"
            for reason in reasons
        )