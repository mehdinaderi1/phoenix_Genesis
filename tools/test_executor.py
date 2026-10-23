"""
Test OrderExecutor end-to-end.
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from exchanges.xt_private_exchange import XTPrivateExchange
from exchanges.xt_exchange import XTExchange
from execution.live.order_executor import OrderExecutor


def log(msg):
    print(f"  {msg}")


def main():
    xt = XTPrivateExchange()
    executor = OrderExecutor(xt, default_timeout=8.0, poll_interval=1.0, logger=log)

    public = XTExchange(timeout=10)
    price = public.get_price("BTCUSDT")
    price = float(price.price if hasattr(price, "price") else price)
    print(f"Current BTC: {price:,.2f}")
    print()

    test_price = f"{price * 0.5:.2f}"
    print(f"Placing BUY LIMIT @ {test_price} (50% below)")
    print()

    result = executor.execute_limit(
        symbol="btc_usdt", side="BUY",
        price=test_price, quantity="0.00013",
        timeout=8.0,
    )

    print()
    print(f"Result: {result}")
    print()

    if result.order_id is None:
        print("FAIL: no order_id")
        return

    print(f"Cancelling {result.order_id}...")
    ok = executor.cancel(result.order_id)
    print(f"  cancel returned: {ok}")
    print()

    time.sleep(1.5)
    orders = xt.get_open_orders("btc_usdt")
    still_open = [o for o in orders if str(o.get("orderId")) == str(result.order_id)]
    print(f"Still open: {len(still_open)}")
    if len(still_open) == 0:
        print()
        print(">>> EXECUTOR + CANCELLATION OK <<<")
    else:
        print(">>> WARNING: still open, cancel manually <<<")


if __name__ == "__main__":
    main()