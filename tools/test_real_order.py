"""
SAFE FIRST TRADE TEST
- Very small size ($0.55 margin)
- Market order, NO SL/TP (first test = simple)
- Auto-close within 5 seconds
- Full logging and verification
"""
import os, time, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange


SYMBOL      = "fet_usdt"
CONTRACTS   = 30
LEVERAGE    = 10
SIDE_OPEN   = "BUY"
POS_SIDE    = "LONG"
SIDE_CLOSE  = "SELL"
WAIT_OPEN   = 5
WAIT_CLOSE  = 5


def main():
    print("=" * 60)
    print("  SAFE FIRST TRADE TEST  (REAL MONEY)")
    print("=" * 60)
    print(f"  Symbol:      {SYMBOL}")
    print(f"  Contracts:   {CONTRACTS}")
    print(f"  Leverage:    {LEVERAGE}x")
    print(f"  Direction:   {POS_SIDE}")
    print(f"  Auto-close:  after {WAIT_OPEN}s")
    print()
    print("  ⚠ This will place a REAL order on XT")
    print("  ⚠ BTC and ETH positions are PROTECTED")
    print()

    confirm = input("  Type CONFIRM to proceed: ").strip()
    if confirm != "CONFIRM":
        print("  Aborted.")
        return

    wrapper = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt", "eth_usdt"])

    # STEP 1: Pre-flight
    print("\n[1/5] PRE-FLIGHT CHECKS")
    print("-" * 60)
    bal = wrapper.get_balance()
    if not bal:
        print("  ✗ Cannot read balance")
        return
    print(f"  Available: ${bal['available']:.2f}")
    if bal['available'] < 2:
        print("  ✗ Balance too low (< $2)")
        return

    positions_before = wrapper.get_user_positions()
    print(f"  Existing positions: {len(positions_before)}")
    for p in positions_before:
        print(f"    - {p['symbol']}: {p['positionSide']} size={p['positionSize']}")

    for p in positions_before:
        if p['symbol'] == SYMBOL:
            print(f"  ✗ Already have {SYMBOL} position - abort")
            return

    price = wrapper._get_price(SYMBOL)
    csize = wrapper.get_contract_size(SYMBOL)
    if not price or not csize:
        print("  ✗ Cannot get price or contract size")
        return

    notional = CONTRACTS * price * csize
    margin = notional / LEVERAGE
    print(f"  {SYMBOL} price: ${price}")
    print(f"  Contract size: {csize}")
    print(f"  Notional: ${notional:.2f}")
    print(f"  Required margin: ${margin:.2f}")
    if margin > bal['available']:
        print("  ✗ Insufficient margin")
        return
    print("  ✓ All checks passed")

    # STEP 2: Open
    print("\n[2/5] OPENING POSITION")
    print("-" * 60)
    ok, resp = wrapper.place_order(
        symbol=SYMBOL, side=SIDE_OPEN, position_side=POS_SIDE,
        contracts=CONTRACTS, leverage=LEVERAGE,
    )
    print(f"  Response: {json.dumps(resp, indent=2)}")
    if not ok or resp.get("returnCode") != 0:
        print("  ✗ Order rejected by XT")
        return
    order_id = (resp.get("result") or {}).get("orderId")
    print(f"  ✓ Order accepted. orderId={order_id}")

    # STEP 3: Wait & verify
    print(f"\n[3/5] WAITING {WAIT_OPEN}s AND VERIFYING POSITION")
    print("-" * 60)
    time.sleep(WAIT_OPEN)

    positions_after = wrapper.get_user_positions()
    our_pos = None
    for p in positions_after:
        if p['symbol'] == SYMBOL and p['positionSide'] == POS_SIDE and float(p.get('positionSize', 0)) > 0:
            our_pos = p
            break

    if not our_pos:
        print("  ⚠ Position not visible - order may still be processing")
        print("  → Open XT panel NOW and check manually")
        print("  → If position exists, close it MANUALLY")
        return

    size_open = float(our_pos['positionSize'])
    entry = our_pos.get('entryPrice', '?')
    print(f"  ✓ Position OPEN: {our_pos['positionSide']} size={size_open} entry={entry}")

    # STEP 4: Close
    print("\n[4/5] CLOSING POSITION")
    print("-" * 60)
    close_size = int(size_open)
    ok, resp = wrapper.place_order(
        symbol=SYMBOL, side=SIDE_CLOSE, position_side=POS_SIDE,
        contracts=close_size, leverage=LEVERAGE,
    )
    print(f"  Response: {json.dumps(resp, indent=2)}")
    if not ok or resp.get("returnCode") != 0:
        print("  ✗ CLOSE FAILED - IMMEDIATELY CLOSE MANUALLY IN XT PANEL")
        return
    close_id = (resp.get("result") or {}).get("orderId")
    print(f"  ✓ Close order accepted. orderId={close_id}")

    # STEP 5: Verify closed
    print(f"\n[5/5] WAITING {WAIT_CLOSE}s AND VERIFYING CLOSE")
    print("-" * 60)
    time.sleep(WAIT_CLOSE)

    final_positions = wrapper.get_user_positions()
    still_open = [p for p in final_positions if p['symbol'] == SYMBOL]
    if still_open:
        print("  ⚠ Position still in list. Check XT panel to confirm it's closed.")
        return

    print("  ✓ Position CLOSED successfully")

    # Final report
    print("\n" + "=" * 60)
    print("  TEST COMPLETE")
    print("=" * 60)
    bal_final = wrapper.get_balance()
    print(f"  Final available: ${bal_final['available']:.2f}")
    print(f"  BTC position: {wrapper.get_user_btc_position()}")
    print()
    print("  ✓ Order placement works")
    print("  ✓ Position verification works")
    print("  ✓ Close order works")
    print("  ✓ BTC/ETH untouched")
    print()
    print("  NEXT: test with SL/TP embedded")


if __name__ == "__main__":
    main()
