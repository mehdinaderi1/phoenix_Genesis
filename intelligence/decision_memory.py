from intelligence.decision_record import DecisionRecord
from intelligence.memory import _persistence


class DecisionMemory:

    def __init__(self, path=None):
        self.path = path if path is not None else None
        if self.path is None:
            self.records = []
        else:
            raw = _persistence.load_records(self.path)
            self.records = [
                _persistence.reconstruct(
                    DecisionRecord, d,
                    defaults={"quality_score": 0},
                )
                for d in raw
            ]

    def store(self, record):
        self.records.append(record)
        if self.path is not None:
            _persistence.append_record(self.path, record)
        return record

    def get_all(self):
        return self.records

    def get_latest(self):
        if not self.records:
            return None
        return self.records[-1]

    def count(self):
        return len(self.records)