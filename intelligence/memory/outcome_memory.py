from intelligence.outcome_record import OutcomeRecord


class OutcomeMemory:


    def __init__(self):

        self.records = []


    def save_outcome(
        self,
        outcome: OutcomeRecord
    ):

        self.records.append(
            outcome
        )


    def get_outcomes(self):

        return self.records