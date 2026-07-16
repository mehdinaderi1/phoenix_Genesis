class StrategyAnalyzer:


    def analyze(self, decision, report):

        score = 0


        # Confidence evaluation
        if decision.confidence >= 80:
            score += 40

        elif decision.confidence >= 60:
            score += 25

        else:
            score += 10



        # Risk evaluation
        if report.risk == "LOW":
            score += 30

        elif report.risk == "MEDIUM":
            score += 20

        else:
            score += 5



        # Action evaluation
        if decision.action in [
            "PREPARE_LONG",
            "PREPARE_SHORT"
        ]:
            score += 30


        return {

            "strategy": decision.action,

            "score": score,

            "confidence": decision.confidence,

            "risk": report.risk,

            "insight":
                self.generate_insight(score)

        }



    def generate_insight(self, score):

        if score >= 80:

            return "High quality strategy"

        elif score >= 50:

            return "Moderate quality strategy"

        else:

            return "Weak strategy"