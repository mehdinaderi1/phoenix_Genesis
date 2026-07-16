class ScenarioEngine:


    def generate(
        self,
        regime,
        confidence,
        risk
    ):

        scenarios = []


        if regime == "TRENDING_BULLISH":

            scenarios.append({

                "name": "BULLISH_CONTINUATION",

                "probability": min(
                    confidence + 5,
                    95
                ),

                "reason":
                    "Bullish trend with supporting confidence"

            })


            scenarios.append({

                "name": "SIDEWAYS",

                "probability": 20,

                "reason":
                    "Market consolidation possibility"

            })


            scenarios.append({

                "name": "BEARISH_REVERSAL",

                "probability": 10,

                "reason":
                    "Trend reversal risk"

            })


        else:

            scenarios.append({

                "name": "UNCERTAIN",

                "probability": 50,

                "reason":
                    "No dominant market regime"

            })


        return scenarios