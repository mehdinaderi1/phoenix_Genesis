"""
Monitor TIA and other fresh candidates every 30 minutes.
Logs changes to data/tia_watch.log
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from exchanges.xt_exchange import XTExchange

# Import scanner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "scan", os.path.join(os.path.dirname(__file__), "scan_trends.py")
)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

WATCH_SYMBOLS = ["TIAUSDT", "INJUSDT", "POLUSDT"]
LOG_PATH = "data/tia_watch.log"

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def check_once():
    ex = XTExchange(timeout=10)
    log("─" * 60)
    for sym in WATCH_SYMBOLS:
        r = scan.score_symbol(ex, sym)
        if r.get("error"):
            log(f"{sym:12s} ERROR: {r['error']}")
            continue
        log(f"{sym:12s} score={r['score']:2d}  HOT={r['hot_score']}  "
            f"ADX={r['adx']}  dir={r['direction']:5s}  "
            f"fresh={r['freshness']:6s}  age={r['age_bars']}b  "
            f"CHG24={r['change_24h']}%")

def main():
    interval = int(os.environ.get("PHOENIX_WATCH_INTERVAL", "1800"))
    max_runs = int(os.environ.get("PHOENIX_WATCH_RUNS", "0"))
    runs = 0
    log(f"WATCH STARTED (interval={interval}s, max_runs={max_runs or 'unlimited'})")
    try:
        while True:
            check_once()
            runs += 1
            if max_runs and runs >= max_runs:
                log(f"WATCH COMPLETE ({runs} runs)")
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        log(f"WATCH INTERRUPTED after {runs} runs")

if __name__ == "__main__":
    main()