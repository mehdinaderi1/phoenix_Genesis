"""
FINAL REAL TEST - SHORT FET at 10x leverage
Verifies actual margin used (not 10x more).
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange


SYMBOL      = "fet_usdt"
CONTRACTS   = 30
LEVERAGE    = 10
POS_SIDE    = "SHORT"
SIDE_OPEN   = "SELL"
SIDE_CLOSE  = "BUY"


def main():
    print("=" * 65)
    print("  FINAL REAL TEST - SHORT FET @ 10x leverage")
    print("=" * 65)

    confirm = input("  Type CONFIRM to proceed: ").strip()
    if confirm != "CONFIRM":
        print("  Aborted.")
        return

    w = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt", "eth_usdt"])

    # Pre-flight
    print("\n[1/6] PRE-FLIGHT")
    print("-" * 65)
    bal_before = w.get_balance()
    print(f"  Available before: ${bal_before['available']:.2f}")
    print(f"  Margin used before: ${bal_before['margin_used']:.2f}")

    # Check no existing FET position
    for p in w.get_user_positions():
        if p['symbol'] == SYMBOL:
            print(f"  X Existing {SYMBOL} position - abort")
            return
    print(f"  No existing {SYMBOL} position - OK")

    price = w._get_price(SYMBOL)
    csize = w.get_contract_size(SYMBOL)
    expected_notional = CONTRACTS * price * csize
    expected_margin = expected_notional / LEVERAGE
    print(f"  Price: ${price}")
    print(f"  Notional: ${expected_notional:.2f}")
    print(f"  Expected margin: ${expected_margin:.2f}")
    print("  All checks passed")

    # Set leverage explicitly
    print("\n[2/6] SET LEVERAGE")
    print("-" * 65)
    ok, resp = w.set_leverage(SYMBOL, POS_SIDE, LEVERAGE)
    if not ok:
        print(f"  X Failed: {resp}")
        return
    lev_now = w.get_leverage(SYMBOL, POS_SIDE)
    print(f"  Leverage set to: {lev_now}x")

    # Open
    print("\n[3/6] OPENING SHORT")
    print("-" * 65)
    ok, resp = w.place_order(
        symbol=SYMBOL, side=SIDE_OPEN, position_side=POS_SIDE,
        contracts=CONTRACTS, leverage=LEVERAGE,
    )
    print(f"  Response: {json.dumps(resp, indent=2)[:300]}")
    if not ok or resp.get("returnCode") not in (0, None):
        print("  X Order failed")
        return
    print("  Order accepted")

    # Verify margin
    print("\n[4/6] VERIFY MARGIN (critical)")
    print("-" * 65)
    time.sleep(5)
    bal_after = w.get_balance()
    print(f"  Available after: ${bal_after['available']:.2f}")
    print(f"  Margin used after: ${bal_after['margin_used']:.2f}")

    margin_delta = bal_after['margin_used'] - bal_before['margin_used']
    print(f"  Margin delta: ${margin_delta:.2f}")
    print(f"  Expected: ${expected_margin:.2f}")
    print(f"  Ratio: {margin_delta / expected_margin:.2f}x")

    if margin_delta > expected_margin * 3:
        print(f"  ⚠⚠⚠ WARNING: Margin is {margin_delta / expected_margin:.0f}x expected!")
        print(f"  → Leverage might still be 1x!")
    elif margin_delta < expected_margin * 0.5:
        print(f"  ⚠ Margin is less than expected - check")
    else:
        print(f"  ✓ Margin matches expected (leverage applied correctly)")

    # Verify position
    our_pos = None
    for p in w.get_user_positions():
        if p['symbol'] == SYMBOL and p['positionSide'] == POS_SIDE:
            our_pos = p
            break
    if our_pos:
        print(f"  ✓ Position: {our_pos['positionSide']} size={our_pos['positionSize']} entry={our_pos.get('entryPrice')}")

    # Close
    print("\n[5/6] CLOSING")
    print("-" * 65)
    if our_pos:
        size = int(float(our_pos['positionSize']))
        ok, resp = w.place_order(
            symbol=SYMBOL, side=SIDE_CLOSE, position_side=POS_SIDE,
            contracts=size, leverage=LEVERAGE,
        )
        print(f"  Close response: {json.dumps(resp, indent=2)[:200]}")
        if not ok:
            print("  X CLOSE FAILED - CLOSE MANUALLY IN XT PANEL NOW")
            return

    # Final
    print("\n[6/6] FINAL VERIFY")
    print("-" * 65)
    time.sleep(5)
    still_open = [p for p in w.get_user_positions() if p['symbol'] == SYMBOL]
    if still_open:
        print("  ⚠ Still open - CHECK PANEL")
        return

    bal_final = w.get_balance()
    print(f"  ✓ Position closed")
    print(f"  Final available: ${bal_final['available']:.2f}")
    print(f"  Total cost: ${bal_before['available'] - bal_final['available']:.4f}")

    print("\n" + "=" * 65)
    print("  COMPLETE")
    print("=" * 65)
    if margin_delta <= expected_margin * 3:
        print("  ✓ Leverage applied correctly")
        print("  ✓ Ready for strategy integration")
    else:
        print("  ✗ Leverage still not applied")
        print("  ✗ Do NOT integrate strategy until fixed")


if __name__ == "__main__":
    main()
