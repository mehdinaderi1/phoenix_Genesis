import os, urllib.request, urllib.parse

token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
chat  = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

print("token:", "SET" if token else "MISSING", f"({len(token)} chars)")
print("chat: ", "SET" if chat else "MISSING", f"({len(chat)} chars)")

if not token or not chat:
    print("ABORT: env vars not set. Run:  . .\\env.local.ps1")
    raise SystemExit(1)

data = urllib.parse.urlencode({"chat_id": chat, "text": "Phoenix test - tunnel OK"}).encode()
url  = f"https://api.telegram.org/bot{token}/sendMessage"
try:
    r = urllib.request.urlopen(url, data=data, timeout=10)
    print("sent: HTTP", r.status)
except Exception as e:
    print("FAILED:", type(e).__name__, e)
