"""
Test BTC re-check logic in isolation.
Simulates a position and calls _add_average directly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_strategy_runner import Runner
from datetime import datetime

print("=" * 60)
print("BTC RE-CHECK LOGIC TEST")
print("=" * 60)

# Create a dry-run runner
r = Runner(dry_run=True)

# Simulate an open LONG position
fake_info = {
    "side": "LONG",
    "size": 100,
    "initial_size": 100,
    "initial_entry": 0.10,
    "entry": 0.10,
    "tp": 0.12,
    "avg_count": 0,
    "avg_entries": [],
    "opened_at": datetime.now().isoformat(),
}

# Fake price at -1.5% (would trigger avg level 1)
fake_price = 0.10 * 0.985  # 0.0985

test_cases = [
    ("DOWN", True),   # Should SKIP (LONG, BTC DOWN)
    ("UP", False),    # Should PROCEED (LONG, BTC UP)
    ("FLAT", False),  # Should PROCEED (LONG, BTC FLAT)
]

for btc_override, expect_skip in test_cases:
    print(f"\n--- Test: BTC = {btc_override} ---")
    os.environ["XT_RUNNER_DRY_BTC_OVERRIDE"] = btc_override
    
    # Copy info to avoid mutation
    test_info = dict(fake_info)
    test_info["avg_entries"] = []
    
    # Call _add_average
    r._add_average("test_usdt", test_info, 0, fake_price)
    
    # Check result
    avg_added = test_info.get("avg_count", 0) > 0
    if expect_skip:
        if avg_added:
            print(f"  FAIL: Expected SKIP, but avg was added")
        else:
            print(f"  PASS: Correctly skipped")
    else:
        if avg_added:
            print(f"  PASS: Correctly added avg (DRY sim)")
        else:
            print(f"  FAIL: Expected proceed, but was skipped")

# Cleanup env
del os.environ["XT_RUNNER_DRY_BTC_OVERRIDE"]
