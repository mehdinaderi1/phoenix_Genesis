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

Regime:
{report.regime}

Signal:
{report.signal}

Confidence:
{report.confidence}%

Risk:
{report.risk}

Decision:
{self._format_decision(report)}

Reasons:
{self._format_reasons(report.reasons)}
"""

    def _format_decision(self, report):

        if report.decision is None:
            return "No decision available"

        output = [
            f"Action: {report.decision.action}",
            f"Reason: {report.decision.reason}",
            f"Confidence: {report.decision.confidence}%"
        ]

        if report.action_proposal:

            output.append(
                f"Validation: {report.action_proposal.status}"
            )

        return "\n".join(output)


    def _format_reasons(self, reasons):

        return "\n".join(
            f"- {reason}"
            for reason in reasons
        )