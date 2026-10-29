import json
with open("data/futures_runner_state_dry.json") as f:
    s = json.load(f)
print("Active positions:", list(s.get("active_positions", {}).keys()))
print("Closed today:", len(s.get("closed_positions", [])))
for sym, info in s.get("active_positions", {}).items():
    print(f"  {sym}: {info['side']} size={info['size']} entry={info['entry']}")
