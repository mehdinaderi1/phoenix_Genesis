"""
Test partial close on XT futures.
Open 60 contracts, close 30, verify remaining 30.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

SYMBOL = "fet_usdt"
OPEN_CONTRACTS = 60
CLOSE_CONTRACTS = 30
LEVERAGE = 10

def main():
    print("=" * 60)
    print("  PARTIAL CLOSE TEST")
    print("=" * 60)
    print(f"  Open: {OPEN_CONTRACTS} contracts")
    print(f"  Close: {CLOSE_CONTRACTS} (half)")
    print(f"  Expected remaining: {OPEN_CONTRACTS - CLOSE_CONTRACTS}")
    print()

    r = input("  Type CONFIRM to proceed: ").strip()
    if r != "CONFIRM":
        print("  Aborted.")
        return

    w = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt", "eth_usdt"])
    
    bal_before = w.get_balance()
    print(f"  Balance before: ${bal_before['available']:.2f}")

    # Set leverage
    w.set_leverage(SYMBOL, "SHORT", LEVERAGE)
    
    # Open 60 SHORT
    print(f"\n[1/4] OPENING {OPEN_CONTRACTS} SHORT")
    ok, resp = w.place_order(
        symbol=SYMBOL, side="SELL", position_side="SHORT",
        contracts=OPEN_CONTRACTS, leverage=LEVERAGE,
    )
    print(f"  {json.dumps(resp, indent=2)[:200]}")
    if not ok:
        print("  X Failed to open")
        return
    time.sleep(3)

    # Verify 60
    print("\n[2/4] VERIFY OPEN")
    pos = None
    for p in w.get_user_positions():
        if p['symbol'] == SYMBOL:
            pos = p
            break
    if not pos:
        print("  X Position not found")
        return
    print(f"  Position: {pos['positionSide']} size={pos['positionSize']}")
    if int(float(pos['positionSize'])) != OPEN_CONTRACTS:
        print(f"  ! Warning: expected {OPEN_CONTRACTS}, got {pos['positionSize']}")

    # Close 30 (partial)
    print(f"\n[3/4] CLOSING {CLOSE_CONTRACTS} (partial)")
    ok, resp = w.place_order(
        symbol=SYMBOL, side="BUY", position_side="SHORT",
        contracts=CLOSE_CONTRACTS, leverage=LEVERAGE,
    )
    print(f"  {json.dumps(resp, indent=2)[:200]}")
    if not ok:
        print("  X Partial close failed")
        # Emergency: close all
        w.place_order(SYMBOL, "BUY", "SHORT", int(pos['positionSize']), LEVERAGE)
        return
    time.sleep(3)

    # Verify remaining
    print("\n[4/4] VERIFY REMAINING")
    pos = None
    for p in w.get_user_positions():
        if p['symbol'] == SYMBOL:
            pos = p
            break
    
    expected_remaining = OPEN_CONTRACTS - CLOSE_CONTRACTS
    
    if not pos:
        print(f"  X All closed (expected {expected_remaining} remaining)")
        return
    
    remaining = int(float(pos['positionSize']))
    print(f"  Remaining: {remaining} contracts")
    if remaining == expected_remaining:
        print(f"  ✓ PARTIAL CLOSE WORKS!")
    else:
        print(f"  ! Expected {expected_remaining}, got {remaining}")
        if remaining > 0:
            # Cleanup: close all
            print(f"  Closing remaining {remaining}...")
            w.place_order(SYMBOL, "BUY", "SHORT", remaining, LEVERAGE)
            time.sleep(2)

    # Final check
    time.sleep(2)
    still_open = [p for p in w.get_user_positions() if p['symbol'] == SYMBOL]
    if still_open:
        print(f"  ! Still open: {still_open[0]['positionSize']} — CLOSE MANUALLY")
    else:
        print("  ✓ Position fully closed")
    
    bal_after = w.get_balance()
    print(f"\n  Balance after: ${bal_after['available']:.2f}")
    print(f"  Cost: ${bal_before['available'] - bal_after['available']:.4f}")


if __name__ == "__main__":
    main()
