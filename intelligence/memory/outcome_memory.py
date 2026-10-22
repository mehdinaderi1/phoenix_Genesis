from intelligence.outcome_record import OutcomeRecord
from intelligence.memory import _persistence


class OutcomeMemory:

    def __init__(self, path=None):
        self.path = path if path is not None else None
        if self.path is None:
            self.records = []
        else:
            raw = _persistence.load_records(self.path)
            self.records = [
                _persistence.reconstruct(OutcomeRecord, d)
                for d in raw
            ]

    def save_outcome(self, outcome: OutcomeRecord):
        self.records.append(outcome)
        if self.path is not None:
            _persistence.append_record(self.path, outcome)

    def get_outcomes(self):
        return self.records