from execution.paper_session_archive import PaperSessionArchive
from execution.paper_session_performance import (
    PaperSessionPerformance
)


class PaperSessionManager:

    def __init__(
        self,
        archive,
        performance=None
    ):
        self.archive = archive
        self.performance = (
            performance
            or PaperSessionPerformance()
        )

    def list_sessions(self):
        return self.archive.list()

    def get_session(self, session_id):
        return self.archive.load(session_id)

    def get_session_summary(self, session_id):
        session = self.get_session(session_id)

        return session.get(
            "summary",
            {}
        )

    def get_session_performance(
        self,
        session_id
    ):
        session = self.get_session(
            session_id
        )

        return self.performance.analyze(
            session
        )