class ExperienceRecord:

    def __init__(
        self,
        regime,
        signal,
        risk,
        success,
        score,
        decision=None,
        strategy=None,
        confidence=0,
        trace=None,
        champion_strategy=None
    ):

        self.regime = regime

        self.signal = signal

        self.risk = risk

        self.success = success

        self.score = score


        # Decision intelligence fields

        self.decision = decision

        self.strategy = strategy

        self.champion_strategy = (
            champion_strategy
            or strategy
        )

        self.confidence = confidence

        self.trace = trace or {}