import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange

ex = XTExchange(timeout=10)

def closes(sym, n=100):
    cs = ex.get_historical_candles(sym, "30m", limit=n)
    if not cs:
        return []
    out = []
    for c in cs:
        if isinstance(c, dict):
            out.append(float(c["close"]))
        elif isinstance(c, (list, tuple)) and len(c) >= 5:
            out.append(float(c[4]))
        elif hasattr(c, "close"):
            out.append(float(c.close))
    return out

btc = closes("BTCUSDT", 100)
zec = closes("ZECUSDT", 100)

print(f"BTC candles: {len(btc)}  |  ZEC candles: {len(zec)}")
print()

if len(btc) < 20 or len(zec) < 20:
    print("Not enough data")
else:
    n = min(len(btc), len(zec))
    btc = btc[-n:]
    zec = zec[-n:]

    btc_ret = [btc[i]/btc[i-1] - 1 for i in range(1, n)]
    zec_ret = [zec[i]/zec[i-1] - 1 for i in range(1, n)]

    # Totals
    btc_total = (btc[-1]/btc[0] - 1) * 100
    zec_total = (zec[-1]/zec[0] - 1) * 100

    print(f"Period: {n} candles (~{n*0.5:.0f} hours)")
    print(f"BTC: {btc[0]:.2f} -> {btc[-1]:.2f}  ({btc_total:+.2f}%)")
    print(f"ZEC: {zec[0]:.2f} -> {zec[-1]:.2f}  ({zec_total:+.2f}%)")
    print()

    # Simple correlation
    mean_b = sum(btc_ret) / len(btc_ret)
    mean_z = sum(zec_ret) / len(zec_ret)
    cov = sum((btc_ret[i]-mean_b)*(zec_ret[i]-mean_z) for i in range(len(btc_ret)))
    var_b = sum((x-mean_b)**2 for x in btc_ret)
    var_z = sum((x-mean_z)**2 for x in zec_ret)
    corr = cov / ((var_b**0.5) * (var_z**0.5)) if var_b*var_z > 0 else 0

    # Full beta
    beta_full = cov / var_b if var_b > 0 else 0

    # Asymmetric beta (user's hypothesis)
    up_pairs = [(btc_ret[i], zec_ret[i]) for i in range(len(btc_ret)) if btc_ret[i] > 0.002]
    dn_pairs = [(btc_ret[i], zec_ret[i]) for i in range(len(btc_ret)) if btc_ret[i] < -0.002]

    up_beta = (
        sum(z/max(b, 1e-9) for b, z in up_pairs) / len(up_pairs)
        if up_pairs else float("nan")
    )
    dn_beta = (
        sum(z/min(b, -1e-9) for b, z in dn_pairs) / len(dn_pairs)
        if dn_pairs else float("nan")
    )

    print(f"Correlation (30m returns): {corr:.3f}")
    print(f"Beta (full): {beta_full:.3f}")
    print()
    print(f"BTC up moves (>0.2%):   {len(up_pairs):2d}  |  up-beta:   {up_beta:+.2f}")
    print(f"BTC down moves (>0.2%): {len(dn_pairs):2d}  |  down-beta: {dn_beta:+.2f}")
    print()

    if up_beta > 1.5 and dn_beta < 0.7 and not (up_beta != up_beta):
        print("=> HYPOTHESIS CONFIRMED: asymmetric positive beta")
    elif corr < 0.3:
        print("=> LOW CORRELATION: ZEC is somewhat independent of BTC")
    elif abs(beta_full) < 0.5:
        print("=> WEAK BETA: ZEC doesn't track BTC reliably")
    else:
        print("=> SYMMETRIC BETA: ZEC amplifies BTC in both directions")