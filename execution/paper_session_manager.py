from execution.paper_session_archive import PaperSessionArchive


class PaperSessionManager:

    def __init__(self, archive):
        self.archive = archive

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
