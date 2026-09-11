from pathlib import Path

from execution.paper_session_store import (
    PaperSessionStore
)


class PaperSessionArchive:

    def __init__(
        self,
        root_path,
        store=None
    ):
        self.root_path = Path(
            root_path
        )

        self.store = (
            store
            or PaperSessionStore()
        )

        self.root_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(
        self,
        session_id,
        session_record
    ):
        path = self.root_path / (
            f"{session_id}.json"
        )

        self.store.save(
            session_record,
            path
        )

    def load(
        self,
        session_id
    ):
        path = self.root_path / (
            f"{session_id}.json"
        )

        return self.store.load(
            path
        )

    def list(
        self
    ):
        return sorted(
            path.stem
            for path in self.root_path.glob(
                "*.json"
            )
        )