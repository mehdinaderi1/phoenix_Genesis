class GovernanceRecord:

    def __init__(
        self,
        strategy,
        status,
        reason=None
    ):
        self.strategy = strategy
        self.status = status
        self.reason = reason


class GovernanceMemory:

    def __init__(self):
        self.records = []

    def save_failure(
        self,
        strategy,
        reason="evolution_blocked"
    ):
        record = GovernanceRecord(
            strategy=strategy,
            status="FAILED",
            reason=reason
        )

        self.records.append(record)

        return record


    def add(self, record):
        self.records.append(record)


    def count(self):
        return len(self.records)


    def latest(self):

        if not self.records:
            return None

        return self.records[-1]