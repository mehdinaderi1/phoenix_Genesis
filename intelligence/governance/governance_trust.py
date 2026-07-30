class GovernanceTrust:


    def calculate(
        self,
        success_rate
    ):


        if success_rate >= 80:

            return {
                "trust": 100,
                "status": "HIGH"
            }


        elif success_rate >= 50:

            return {
                "trust": 70,
                "status": "MEDIUM"
            }


        return {
            "trust": 30,
            "status": "LOW"
        }