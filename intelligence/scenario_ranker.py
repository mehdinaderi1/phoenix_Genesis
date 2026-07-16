class ScenarioRanker:


    def rank(self, scenarios):

        if not scenarios:

            return None


        ranked = sorted(

            scenarios,

            key=lambda x: x["probability"],

            reverse=True

        )


        primary = ranked[0]


        return {

            "primary_scenario":
                primary["name"],

            "probability":
                primary["probability"],

            "reason":
                primary["reason"],

            "all_scenarios":
                ranked

        }