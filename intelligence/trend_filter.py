from config.settings import Settings


def _extract_closes(candles):
    """لیست close از هر فرمت ورودی"""
    if candles is None:
        return None

    closes = []

    # DataFrame (اگر pandas نصب باشد)
    if hasattr(candles, "columns") and hasattr(candles, "__getitem__"):
        try:
            if "close" in candles.columns:
                return [float(x) for x in candles["close"].tolist()]
        except Exception:
            pass

    if not isinstance(candles, (list, tuple)) or len(candles) == 0:
        return None

    first = candles[0]

    # لیست دیکشنری
    if isinstance(first, dict):
        for c in candles:
            if "close" in c:
                closes.append(float(c["close"]))
        return closes or None

    # لیست لیست/تاپل — [ts, open, high, low, close, volume]
    if isinstance(first, (list, tuple)) and len(first) >= 5:
        for c in candles:
            closes.append(float(c[4]))
        return closes or None

    return None


def _ema_series(closes, span):
    """EMA با فرمول استاندارد (alpha = 2/(span+1))"""
    if not closes or span <= 0:
        return []
    alpha = 2.0 / (span + 1.0)
    out = [closes[0]]
    for price in closes[1:]:
        out.append(alpha * price + (1.0 - alpha) * out[-1])
    return out


def passes_trend_filter(candles):
    """
    برمی‌گرداند (allow_long, allow_short).
    - اگر TREND_FILTER_ENABLED=False → (True, True)
    - اگر کندل کافی نبود → (True, True) با لاگ
    """
    if not getattr(Settings, "TREND_FILTER_ENABLED", False):
        return True, True

    closes = _extract_closes(candles)
    if not closes:
        print("[TREND] no candles → permissive")
        return True, True

    fast = getattr(Settings, "EMA_FAST", 50)
    slow = getattr(Settings, "EMA_SLOW", 200)

    if len(closes) < slow + 1:
        print(f"[TREND] not enough candles ({len(closes)}<{slow}) → permissive")
        return True, True

    ema_fast_series = _ema_series(closes, fast)
    ema_slow_series = _ema_series(closes, slow)

    ema_fast = ema_fast_series[-1]
    ema_slow = ema_slow_series[-1]
    price = closes[-1]

    # ─── منطق استاندارد golden/death cross ───
    # فقط مقایسهٔ EMA ها (بدون price که در recovery گیج‌کننده است)
    if ema_fast > ema_slow:
        allow_long = True
        allow_short = False
    elif ema_fast < ema_slow:
        allow_long = False
        allow_short = True
    else:
        # برابر — به هر دو جهت اجازه بده (به‌ندرت)
        allow_long = True
        allow_short = True
    # ─────────────────────────────────────────
    print(
        f"[TREND] price={price:.2f} "
        f"ema_fast={ema_fast:.2f} ema_slow={ema_slow:.2f} "
        f"→ long={allow_long} short={allow_short}"
    )

    return allow_long, allow_short