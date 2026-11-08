"""
tools/check_vpn.py — Monitor Python's outbound IP; alert on VPN drop
"""
import sys, os, time, urllib.request, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifications.telegram_sender import TelegramSender

CHECK_INTERVAL_SEC = 300   # 5 minutes

def get_ip():
    try:
        with urllib.request.urlopen("https://httpbin.org/ip", timeout=10) as r:
            data = json.loads(r.read())
            return data.get("origin", "")
    except Exception as e:
        return f"ERR:{type(e).__name__}"

def is_uk_ip(ip):
    # IPهای انگلیس و هلند هر دو سالم هستند
    return ip.startswith("91.231.") or ip.startswith("37.156.155.") or ip.startswith("62.106.")

def safe_send(notifier, msg):
    """ارسال پیام با مدیریت خطا (اگر اینترنت قطع بود، کرش نکن)"""
    try:
        notifier.send_message(msg)
        print(f"[VPN-Check] Message sent: {msg.splitlines()[0]}")
    except Exception as e:
        print(f"[VPN-Check] Could not send Telegram message: {e}")

def main():
    notifier = TelegramSender()
    last_state = None
    
    print(f"[VPN-Check] Started. Interval={CHECK_INTERVAL_SEC}s")
    while True:
        ip = get_ip()
        ok = is_uk_ip(ip)
        state = "UK" if ok else "BAD"
        ts = datetime.now().strftime("%H:%M")

        print(f"[{ts}] IP={ip}  state={state}")

        # فقط وقتی وضعیت تغییر کرد، پیام بفرست
        if state != last_state:
            if state == "BAD":
                safe_send(notifier, 
                    f"🚨 VPN DOWN\n"
                    f"Time: {ts}\n"
                    f"Python IP: {ip}\n"
                    f"Bot cannot reach XT. Check WireSock."
                )
            else:
                safe_send(notifier, 
                    f"✅ VPN restored\nTime: {ts}\nIP: {ip}"
                )
            last_state = state

        time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    main()