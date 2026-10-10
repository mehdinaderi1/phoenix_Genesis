import json
from unittest.mock import patch

from notifications.telegram_sender import TelegramSender


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_send_message_returns_result_after_api_success():
    sender = TelegramSender(token="test-token", chat_id="12345")
    api_result = {"message_id": 77, "text": "Phoenix test"}

    with patch(
        "notifications.telegram_sender.urlopen",
        return_value=FakeResponse({"ok": True, "result": api_result}),
    ) as mock_urlopen:
        result = sender.send_message("Phoenix test")

    assert result == api_result
    request = mock_urlopen.call_args.args[0]
    body = json.loads(request.data.decode("utf-8"))
    assert body["chat_id"] == "12345"
    assert body["text"] == "Phoenix test"
    assert request.full_url.endswith("/sendMessage")


def test_send_message_raises_when_api_does_not_confirm_success():
    sender = TelegramSender(token="test-token", chat_id="12345")

    with patch(
        "notifications.telegram_sender.urlopen",
        return_value=FakeResponse({"ok": False, "description": "rejected"}),
    ):
        try:
            sender.send_message("Phoenix test")
            assert False, "Unconfirmed delivery must raise an error"
        except RuntimeError as exc:
            assert "did not confirm" in str(exc)


def test_sender_requires_credentials():
    with patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""},
    ):
        try:
            TelegramSender()
            assert False, "Missing credentials must be rejected"
        except ValueError as exc:
            assert "TELEGRAM_BOT_TOKEN" in str(exc)


def test_sender_rejects_empty_message():
    sender = TelegramSender(token="test-token", chat_id="12345")

    try:
        sender.send_message("   ")
        assert False, "Empty message must be rejected"
    except ValueError as exc:
        assert "must not be empty" in str(exc)
