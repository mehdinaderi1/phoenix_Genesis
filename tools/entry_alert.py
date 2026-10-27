# tools/entry_alert.py
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange

FET_ENTRY_LOW  = 0.1760
FET_ENTRY_HIGH = 0.1790
ZEC_ENTRY_LOW  = 1250.0
ZEC_ENTRY_HIGH = 1265.0

def main():
    ex = XTExchange(timeout=10)
    print(f"ALERT: FET [{FET_ENTRY_LOW}-{FET_ENTRY_HIGH}]  ZEC [{ZEC_ENTRY_LOW}-{ZEC_ENTRY_HIGH}]")
    print("Ctrl+C to stop\n")

    while True:
        try:
            fet = ex.get_price("FETUSDT")
            zec = ex.get_price("ZECUSDT")
            fp = getattr(fet, "price", fet)
            zp = getattr(zec, "price", zec)

            fet_alert = FET_ENTRY_LOW <= fp <= FET_ENTRY_HIGH
            zec_alert = ZEC_ENTRY_LOW <= zp <= ZEC_ENTRY_HIGH

            ts = time.strftime("%H:%M:%S")
            marker = ""
            if fet_alert:
                marker += " 🔔FET"
            if zec_alert:
                marker += " 🔔ZEC"
            print(f"[{ts}] FET={fp:.4f}  ZEC={zp:.2f}{marker}")

            if fet_alert or zec_alert:
                print("  ⚠ ENTRY ZONE REACHED")
        except Exception as e:
            print(f"error: {e}")
        time.sleep(300)  # 5 min

if __name__ == "__main__":
    main()