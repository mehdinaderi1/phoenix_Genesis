import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramSender:
    """Minimal outbound-only Telegram Bot API adapter."""

    def __init__(self, token=None, chat_id=None, timeout=10):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.timeout = timeout

        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is not configured")

    def send_message(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Telegram message text must not be empty")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        body = json.dumps({
            "chat_id": self.chat_id,
            "text": text,
        }).encode("utf-8")

        request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(
                f"Telegram API returned HTTP {exc.code}"
            ) from None
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Telegram delivery failed: {type(exc).__name__}"
            ) from None

        if result.get("ok") is not True:
            raise RuntimeError("Telegram API did not confirm message delivery")

        return result["result"]
