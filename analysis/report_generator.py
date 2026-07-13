class ReportGenerator:

    def generate(self, asset, signals, confidence, decision, risk):

        report = {
            "asset": asset,
            "signals": signals,
            "confidence": confidence,
            "decision": decision,
            "risk": risk
        }

        return report