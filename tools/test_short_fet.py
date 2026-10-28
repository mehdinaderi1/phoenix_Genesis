"""
SAFE FIRST SHORT TEST
- SHORT on FET (not protected)
- Small size, auto-close in 5s
"""
import os, time, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange


SYMBOL      = "fet_usdt"
CONTRACTS   = 30
LEVERAGE    = 10
SIDE_OPEN   = "SELL"
POS_SIDE    = "SHORT"
SIDE_CLOSE  = "BUY"
WAIT_OPEN   = 5
WAIT_CLOSE  = 5


def main():
    print("=" * 60)
    print("  SAFE FIRST SHORT TEST  (REAL MONEY)")
    print("=" * 60)
    print(f"  Symbol:    {SYMBOL}")
    print(f"  Contracts: {CONTRACTS}")
    print(f"  Leverage:  {LEVERAGE}x")
    print(f"  Direction: {POS_SIDE}")
    print(f"  Protected: btc_usdt, eth_usdt")
    print()

    confirm = input("  Type CONFIRM to proceed: ").strip()
    if confirm != "CONFIRM":
        print("  Aborted.")
        return

    wrapper = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt", "eth_usdt"])

    print("\n[1/5] PRE-FLIGHT")
    print("-" * 60)
    bal = wrapper.get_balance()
    print(f"  Available: ${bal['available']:.2f}")

    for p in wrapper.get_user_positions():
        if p['symbol'] == SYMBOL:
            print(f"  X Already have {SYMBOL} position - abort")
            return
    print(f"  No existing {SYMBOL} position - OK")

    price = wrapper._get_price(SYMBOL)
    csize = wrapper.get_contract_size(SYMBOL)
    if not price or not csize:
        print("  X Cannot get price")
        return

    notional = CONTRACTS * price * csize
    margin = notional / LEVERAGE
    print(f"  Price: ${price}")
    print(f"  Notional: ${notional:.2f}")
    print(f"  Margin: ${margin:.2f}")
    print("  All checks passed")

    print("\n[2/5] OPENING SHORT")
    print("-" * 60)
    ok, resp = wrapper.place_order(
        symbol=SYMBOL, side=SIDE_OPEN, position_side=POS_SIDE,
        contracts=CONTRACTS, leverage=LEVERAGE,
    )
    print(f"  Response: {json.dumps(resp, indent=2)[:400]}")
    if not ok:
        print("  X Order rejected")
        return
    if resp.get("returnCode") not in (0, None):
        print(f"  X returnCode={resp.get('returnCode')}")
        return
    print("  Order accepted")

    print(f"\n[3/5] WAIT {WAIT_OPEN}s AND VERIFY")
    print("-" * 60)
    time.sleep(WAIT_OPEN)

    our_pos = None
    for p in wrapper.get_user_positions():
        if p['symbol'] == SYMBOL and p['positionSide'] == POS_SIDE and float(p.get('positionSize', 0)) > 0:
            our_pos = p
            break

    if not our_pos:
        print("  Position not visible - CHECK XT PANEL NOW")
        return

    size = float(our_pos['positionSize'])
    print(f"  SHORT OPEN: size={size} entry={our_pos.get('entryPrice')}")

    print("\n[4/5] CLOSING SHORT")
    print("-" * 60)
    ok, resp = wrapper.place_order(
        symbol=SYMBOL, side=SIDE_CLOSE, position_side=POS_SIDE,
        contracts=int(size), leverage=LEVERAGE,
    )
    print(f"  Response: {json.dumps(resp, indent=2)[:400]}")
    if not ok:
        print("  X CLOSE FAILED - CLOSE MANUALLY IN XT NOW")
        return
    print("  Close order accepted")

    print(f"\n[5/5] WAIT {WAIT_CLOSE}s AND VERIFY CLOSE")
    print("-" * 60)
    time.sleep(WAIT_CLOSE)

    still_open = [p for p in wrapper.get_user_positions() if p['symbol'] == SYMBOL]
    if still_open:
        print("  Still in position list - CHECK XT PANEL")
        return
    print("  Position CLOSED")

    print("\n" + "=" * 60)
    print("  SHORT TEST COMPLETE")
    print("=" * 60)
    print("  SHORT direction works")
    print("  Close works")
    print("  BTC/ETH untouched")
    print()
    print("  NEXT: test with SL/TP embedded")


if __name__ == "__main__":
    main()
