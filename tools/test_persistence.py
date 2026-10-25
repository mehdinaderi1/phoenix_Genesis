"""
Persistence test — two-process simulation.
Run twice: first creates position, second recovers it.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from execution.live.live_execution_adapter import LiveExecutionAdapter

STATE = "data/_test_live_positions.json"


def cleanup():
    if Path(STATE).exists():
        Path(STATE).unlink()


def run1():
    print("=== RUN 1: create and save ===")
    cleanup()
    a = LiveExecutionAdapter(dry_run=True, state_path=STATE)
    a.load_state()
    r = a.open_position("btc_usdt", "BUY", 81000, 0.00013, sl=79000, tp=83000)
    print(f"Open: {r['action']}")
    print(f"  file exists: {Path(STATE).exists()}")
    print(f"  file size: {Path(STATE).stat().st_size if Path(STATE).exists() else 0} bytes")
    print(f"  has_position: {a.has_position('btc_usdt')}")
    print()


def run2():
    print("=== RUN 2: load and recover ===")
    a = LiveExecutionAdapter(dry_run=True, state_path=STATE)
    ok = a.load_state()
    print(f"Load returned: {ok}")
    print(f"  has_position: {a.has_position('btc_usdt')}")
    pos = a.get_position("btc_usdt")
    if pos:
        print(f"  recovered: {pos.side} {pos.quantity} @ {pos.entry_price}")
        print(f"  sl={pos.sl} tp={pos.tp}")
        print(f"  opened_at: {pos.opened_at.isoformat()}")
    else:
        print("  NO POSITION — persistence FAILED")
        return

    # close and verify save
    print()
    print("=== Closing recovered position ===")
    r = a.close_position("btc_usdt", current_price=82000, reason="test")
    print(f"Close: {r['action']} PnL={r.get('realized_pnl', 0):+.6f}")
    print(f"  has_position: {a.has_position('btc_usdt')}")

    # Verify file updated (should be empty now)
    import json
    data = json.loads(Path(STATE).read_text(encoding="utf-8"))
    print(f"  file positions after close: {len(data['positions'])}")
    print()
    print(">>> PERSISTENCE OK <<<")

    cleanup()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode in ("1", "both"):
        run1()
    if mode in ("2", "both"):
        # If "both", run2 in a subprocess to prove it's a fresh load
        if mode == "both":
            import subprocess
            subprocess.run([sys.executable, __file__, "2"], check=False)
        else:
            run2()