import json


class PaperSessionSerializer:

    def serialize(
        self,
        session_record
    ):
        return json.dumps(
            session_record
        )