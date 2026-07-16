class DecisionQualityAnalyzer:


    def calculate(self, record):

        score = 0


        # Confidence Score
        if record.confidence >= 80:

            score += 40

        elif record.confidence >= 60:

            score += 25

        else:

            score += 10



        # Risk Score
        if record.risk == "LOW":

            score += 30

        elif record.risk == "MEDIUM":

            score += 20

        else:

            score += 5



        # Validation Score
        if record.validation_status == "APPROVED":

            score += 30


        else:

            score += 0



        return {

            "symbol": record.symbol,

            "action": record.action,

            "quality_score": score

        }