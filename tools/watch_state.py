"""
Watch runner state every 5 minutes, log to file.
Run in terminal 2 while runner runs in terminal 1.
"""
import sys, os, json, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOG_FILE = "data/runner_watch.log"
INTERVAL = 300  # 5 minutes

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    os.makedirs("data", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def check():
    try:
        with open("data/futures_runner_state_dry.json") as f:
            s = json.load(f)
    except Exception as e:
        log(f"ERROR reading state: {e}")
        return
    
    active = s.get("active_positions", {})
    closed = s.get("closed_positions", [])
    
    if active:
        for sym, info in active.items():
            log(f"ACTIVE {sym}: {info['side']} size={info['size']} entry={info['entry']}")
    else:
        log("No active positions")
    
    log(f"Closed today: {len(closed)}")
    if closed:
        last = closed[-1]
        log(f"  Last: {last.get('symbol')} {last.get('side')} {last.get('reason')} PnL=${last.get('pnl_usdt', 0):+.4f}")

if __name__ == "__main__":
    print(f"Watching state every {INTERVAL}s. Ctrl+C to stop.")
    print(f"Log: {LOG_FILE}\n")
    log("=" * 40)
    log("Watcher started")
    try:
        while True:
            check()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        log("Watcher stopped")
