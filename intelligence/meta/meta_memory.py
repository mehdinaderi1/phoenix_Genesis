from intelligence.meta.meta_feedback import MetaFeedbackRecord
from intelligence.memory import _persistence


class MetaMemory:

    def __init__(self, path=None):
        self.path = path if path is not None else None
        if self.path is None:
            self.records = []
        else:
            raw = _persistence.load_records(self.path)
            self.records = [
                _persistence.reconstruct(MetaFeedbackRecord, d)
                for d in raw
            ]

    def store(self, record):
        self.records.append(record)
        if self.path is not None:
            _persistence.append_record(self.path, record)

    def get_records(self):
        return self.records

    def count(self):
        return len(self.records)