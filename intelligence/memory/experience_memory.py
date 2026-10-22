import os
from pathlib import Path

from intelligence.experience_record import ExperienceRecord
from intelligence.memory import _persistence


def _default_path():
    return os.environ.get(
        "PHOENIX_EXPERIENCE_MEMORY_PATH",
        "data/memory/experiences.jsonl",
    )


class ExperienceMemory:

    def __init__(self, path=None):
        # path=None  →  RAM-only (سازگار با تست‌های موجود)
        # path="..." →  file-backed (استفاده در production)
        self.path = path if path is not None else None
        if self.path is None:
            self.experiences = []
        else:
            raw = _persistence.load_records(self.path)
            self.experiences = [
                _persistence.reconstruct(ExperienceRecord, d)
                for d in raw
            ]

    @property
    def records(self):
        return self.experiences

    def save_experience(self, experience: ExperienceRecord):
        self.experiences.append(experience)
        if self.path is not None:
            _persistence.append_record(self.path, experience)

    def get_experiences(self):
        return self.experiences

    def find_by_strategy(self, strategy: str):
        return [
            exp for exp in self.experiences
            if getattr(exp, "strategy", None) == strategy
        ]

    def find_similar(self, strategy: str, success=None):
        results = []
        for exp in self.experiences:
            if getattr(exp, "strategy", None) != strategy:
                continue
            if success is not None and exp.success != success:
                continue
            results.append(exp)
        return results