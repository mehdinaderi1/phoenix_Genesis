import json


class PaperSessionSerializer:

    def serialize(
        self,
        session_record
    ):
        return json.dumps(
            session_record
        )

    def deserialize(
        self,
        serialized_data
    ):
        return json.loads(
            serialized_data
        )