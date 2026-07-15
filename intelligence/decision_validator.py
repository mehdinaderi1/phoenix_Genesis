class DecisionValidator:


    def validate(self, decision):

        if decision.action == "WAIT":
            return False


        if decision.confidence < 70:
            return False


        return True