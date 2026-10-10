"""Append-only JSONL journal for observed market opportunities."""

import json
from pathlib import Path


class OpportunityJournal:
    """Persist opportunity records without making trading decisions."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, opportunity):
        """Append one opportunity record as a JSONL entry."""
        if not isinstance(opportunity, dict):
            raise TypeError("opportunity must be a dict")

        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    opportunity,
                    ensure_ascii=False,
                    allow_nan=False,
                )
            )
            stream.write("\n")

    def read_all(self):
        """Read all opportunity records in append order."""
        if not self.path.exists():
            return []

        records = []
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSONL record at line {line_number}"
                    ) from exc

                if not isinstance(record, dict):
                    raise ValueError(
                        f"Journal record at line {line_number} must be an object"
                    )
                records.append(record)

        return records
