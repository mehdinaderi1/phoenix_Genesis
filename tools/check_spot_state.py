import json
s = json.load(open("data/spot_runner_state_dry.json"))
print("Active:", list(s["positions"].keys()))
print("Closed:", len(s.get("closed", [])))
for k, v in s["positions"].items():
    print(f"  {k}: levels={v['levels_filled']} avg={v['avg_entry']:.6g} size={v['size']:.2f}")
