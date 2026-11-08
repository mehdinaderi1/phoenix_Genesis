"""
tools/build_ratio_data.py — Calculate Alt/BTC ratio for all symbols
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = [
    "ETHUSDT","OPUSDT","DOGEUSDT","PEPEUSDT","AAVEUSDT","INJUSDT",
    "FETUSDT","WLDUSDT","ZECUSDT","XRPUSDT","DASHUSDT"
]
DATA_DIR = "data/historical"

def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "ts": int(float(r["timestamp"])),
                "close": float(r["close"])
            })
    rows.sort(key=lambda x: x["ts"])
    return rows

def main():
    btc_path = os.path.join(DATA_DIR, "BTCUSDT_4H.csv")
    if not os.path.exists(btc_path):
        print("ERROR: BTCUSDT_4H.csv not found")
        return
    btc = load_csv(btc_path)
    btc_dict = {r["ts"]: r["close"] for r in btc}

    for sym in SYMBOLS:
        path = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        if not os.path.exists(path):
            continue
        rows = load_csv(path)
        out = []
        for r in rows:
            if r["ts"] in btc_dict and btc_dict[r["ts"]] > 0:
                ratio = r["close"] / btc_dict[r["ts"]]
                out.append((r["ts"], ratio))
        
        if not out:
            print(f"{sym}: no matching BTC timestamps")
            continue
        
        out_path = os.path.join(DATA_DIR, f"{sym.replace('USDT','')}_BTC_ratio.csv")
        with open(out_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "ratio"])
            w.writerows(out)
        print(f"{sym}: {len(out)} ratio candles -> {out_path}")

if __name__ == "__main__":
    main()