import json
s = json.load(open("data/futures_runner_state_dry.json"))
print("Active positions:", len(s.get("active_positions", {})))
for k, v in s.get("active_positions", {}).items():
    print(f"  {k}: {v['side']} size={v['size']} entry={v['entry']:.6g} avg={v.get('avg_count',0)}")
print("Closed today:", len(s.get("closed_positions", [])))
for c in s.get("closed_positions", [])[-5:]:
    print(f"  {c['symbol']} {c['side']} reason={c['reason']} pnl={c['pnl_usdt']:+.2f}$")
print("last_btc_dir:", s.get("last_btc_dir", "?"))
