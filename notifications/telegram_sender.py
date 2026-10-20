import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramSender:
    """Minimal outbound-only Telegram Bot API adapter."""

    def __init__(self, token=None, chat_id=None, timeout=10):
        self.token = (token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
        self.chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
        self.timeout = timeout

        # ─── Sanitize: فقط ASCII مجاز باشد ───
        self.token = self.token.encode("ascii", errors="ignore").decode("ascii")
        self.chat_id = self.chat_id.encode("ascii", errors="ignore").decode("ascii")

        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is not configured")

    def send_message(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Telegram message text must not be empty")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}

        # ─── ensure_ascii=True: JSON با \uXXXX escape، ASCII-safe ───
        try:
            body = json.dumps(payload, ensure_ascii=True).encode("ascii")
        except UnicodeEncodeError as exc:
            # Fallback: اجباراً به ASCII با replacement
            safe_text = text.encode("ascii", errors="replace").decode("ascii")
            payload = {"chat_id": self.chat_id, "text": safe_text}
            body = json.dumps(payload, ensure_ascii=True).encode("ascii")

        request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                detail = ""
            raise RuntimeError(f"Telegram HTTP {exc.code}: {detail}") from None
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Telegram delivery failed: {type(exc).__name__}: {exc}"
            ) from None

        if result.get("ok") is not True:
            raise RuntimeError(f"Telegram API did not confirm delivery: {result}")

        return result["result"]


def send_message(self, text, max_retries=2):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Telegram message text must not be empty")

    url = f"https://api.telegram.org/bot{self.token}/sendMessage"
    payload = {"chat_id": self.chat_id, "text": text}
    body = json.dumps(payload, ensure_ascii=True).encode("ascii")

    last_exc = None
    for attempt in range(1, max_retries + 1):
        request = Request(
            url, data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("ok") is True:
                    return result["result"]
                raise RuntimeError(
                    f"Telegram API did not confirm delivery: {result}"
                )
        except HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                detail = ""
            # خطاهای 4xx تلگرام قابل retry نیستند
            if 400 <= exc.code < 500 and exc.code != 429:
                raise RuntimeError(
                    f"Telegram HTTP {exc.code}: {detail}"
                ) from None
            last_exc = RuntimeError(f"Telegram HTTP {exc.code}: {detail}")
        except (URLError, TimeoutError, OSError) as exc:
            last_exc = RuntimeError(
                f"Telegram delivery failed: {type(exc).__name__}: {exc}"
            )
        if attempt < max_retries:
            import time
            time.sleep(2 * attempt)   # 2s, 4s

    raise last_exc