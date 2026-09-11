from pathlib import Path

from execution.paper_session_serializer import (
    PaperSessionSerializer
)


class PaperSessionStore:

    def __init__(
        self,
        serializer=None
    ):
        self.serializer = (
            serializer
            or PaperSessionSerializer()
        )

    def save(
        self,
        session_record,
        path
    ):
        serialized_data = self.serializer.serialize(
            session_record
        )

        Path(path).write_text(
            serialized_data,
            encoding="utf-8"
        )

    def load(
        self,
        path
    ):
        serialized_data = Path(path).read_text(
            encoding="utf-8"
        )

        return self.serializer.deserialize(
            serialized_data
        )