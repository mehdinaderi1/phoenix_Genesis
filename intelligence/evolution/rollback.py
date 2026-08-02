class RollbackResult:
    def __init__(self, executed: bool, reason: str):
        self.executed = executed
        self.reason = reason


class RollbackManager:

    def __init__(self):
        self.executed = False
        self.history = []

    def rollback(self, strategy_version, reason="performance_drop"):

        self.executed = True

        record = {
            "strategy": strategy_version,
            "reason": reason
        }

        self.history.append(record)

        return RollbackResult(
            executed=True,
            reason=reason
        )

    def count(self):
        return len(self.history)