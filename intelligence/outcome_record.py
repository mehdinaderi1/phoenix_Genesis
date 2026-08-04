class OutcomeRecord:


    def __init__(
        self,
        decision,
        entry_price,
        exit_price,
        timestamp=None
    ):

        self.decision = decision

        self.entry_price = entry_price

        self.exit_price = exit_price

        self.timestamp = timestamp