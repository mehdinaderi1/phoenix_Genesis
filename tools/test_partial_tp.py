"""
Synthetic test for Partial TP logic.
Simulates a position near half-TP and calls _check_partial_tp.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_strategy_runner import Runner
from datetime import datetime

print("=" * 60)
print("PARTIAL TP LOGIC TEST")
print("=" * 60)

r = Runner(dry_run=True)

# Simulated LONG position
# Entry: 0.10, TP: 0.12 → half_tp = 0.10 + 0.02*0.5 = 0.11
base_info = {
    "side": "LONG",
    "size": 100,
    "initial_size": 100,
    "initial_entry": 0.10,
    "entry": 0.10,
    "tp": 0.12,
    "avg_count": 0,
    "avg_entries": [],
    "partial_taken": False,
    "opened_at": datetime.now().isoformat(),
}

test_cases = [
    ("Below half-TP", 0.105, False),   # Should NOT trigger
    ("At half-TP",    0.110, True),    # Should trigger (50% of TP)
    ("Above half-TP", 0.115, True),    # Should trigger
    ("At full TP",    0.120, True),    # Should trigger (but partial first)
]

for name, price, expect in test_cases:
    print(f"\n--- {name}: price={price} ---")
    info = dict(base_info)
    info["avg_entries"] = []
    info["partial_taken"] = False
    info["size"] = 100
    
    r._check_partial_tp("test_usdt", info, price)
    
    triggered = info.get("partial_taken", False)
    if expect and triggered:
        print(f"  PASS: Partial TP triggered, size now {info['size']}")
    elif not expect and not triggered:
        print(f"  PASS: Correctly not triggered")
    else:
        print(f"  FAIL: expected={'trigger' if expect else 'no trigger'}, got {'trigger' if triggered else 'no trigger'}")

# Test: don't trigger twice
print("\n--- Test: doesn't trigger twice ---")
info = dict(base_info)
info["avg_entries"] = []
info["partial_taken"] = False
info["size"] = 100
r._check_partial_tp("test_usdt", info, 0.115)  # first trigger
size_after_first = info["size"]
r._check_partial_tp("test_usdt", info, 0.118)  # second call
if info["size"] == size_after_first:
    print(f"  PASS: Only triggered once, size stayed {info['size']}")
else:
    print(f"  FAIL: Triggered again, size={info['size']}")

# Test: skip if averages active
print("\n--- Test: skip if averages active ---")
info = dict(base_info)
info["avg_entries"] = []
info["partial_taken"] = False
info["avg_count"] = 1
info["size"] = 200
r._check_partial_tp("test_usdt", info, 0.115)
if not info.get("partial_taken"):
    print(f"  PASS: Skipped (avg_count=1)")
else:
    print(f"  FAIL: Should skip when averages active")
