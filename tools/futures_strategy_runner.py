"""
Futures Strategy Runner - Fully Automated Pullback Trading
============================================================
Strategy:
  1. BTC direction filter (never trade against BTC)
  2. Channel edge entry (4H Donchian)
  3. Pullback confirmation (candle wick)
  4. SL at channel edge + buffer, TP at channel mid

Safety:
  - MAX_POSITIONS default 1
  - Daily loss limit 3%
  - STOP_TRADING file kills runner
  - BTC/ETH protected (skip_symbols)
  - DRY_RUN=1 by default (set XT_FUTURES_LIVE=1 for real)

Usage:
  # Dry run (observe for 10-30 min):
  python tools\futures_strategy_runner.py
  
  # Live trading (requires typing LIVE at prompt):
  $env:XT_FUTURES_LIVE = "1"
  python tools\futures_strategy_runner.py
"""
import os, sys, time, json
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from tools.futures_wrapper_v2 import XTFuturesExchange

# ═══════════════════════════════════════════════════════════
# AVERAGING CONFIG (user's strategy)
# ═══════════════════════════════════════════════════════════
AVG_ENABLED = os.environ.get("XT_RUNNER_AVG_ENABLED", "1") == "1"
AVG_LEVELS_PCT = [1.5, 3.5]      # فاصله پله‌ها از entry اولیه
AVG_SIZE_MULT = [1.0, 1.0]       # اندازه هر پله (نسبت به entry اولیه)
HARD_SL_PCT = 5.0                # حد ضرر سخت
REMOVE_AVG_AT_BE = True          # برداشتن میانگین در breakeven
TRAILING_ENABLED = False
TRAILING_START_PCT = 1.0
TRAILING_DISTANCE_PCT = 0.5
ALLOW_SHORT = os.environ.get("XT_RUNNER_ALLOW_SHORT", "0") == "1"
# ═══════════════════════════════════════════════════════════
# SIGNAL GENERATOR CONFIG
# ═══════════════════════════════════════════════════════════
MAX_SIGNALS_DISPLAY = int(os.environ.get("XT_RUNNER_MAX_SIGNALS", "10"))
SIGNAL_ALERT_EVERY = int(os.environ.get("XT_RUNNER_SIGNAL_EVERY", "10"))

# ═══════════════════════════════════════════════════════════
# PARTIAL TP CONFIG
# ═══════════════════════════════════════════════════════════
PARTIAL_TP_ENABLED = os.environ.get("XT_RUNNER_PARTIAL_TP", "1") == "1"
PARTIAL_TP_AT_PCT = float(os.environ.get("XT_RUNNER_PARTIAL_TP_AT", "50"))
PARTIAL_TP_FRACTION = float(os.environ.get("XT_RUNNER_PARTIAL_TP_FRAC", "0.5"))


# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

SYMBOLS = [
    # L1
    "ETHUSDT", "SOLUSDT",
    # L2
    "ARBUSDT", "OPUSDT",
    # Meme
    "DOGEUSDT", "PEPEUSDT",
    # DeFi
    "AAVEUSDT", "INJUSDT",
    # AI
    "FETUSDT", "WLDUSDT",
    # Privacy
    "ZECUSDT", "XMRUSDT",
    # Payments
    "XRPUSDT", "DASHUSDT",
]

TIMEFRAME = "4H"
CHANNEL_PERIOD = 30
MIN_WIDTH_PCT = 3.0
MAX_WIDTH_PCT = 20.0
LONG_MAX_POS = 25.0
SHORT_MIN_POS = 75.0

LEVERAGE = int(os.environ.get("XT_RUNNER_LEVERAGE", "10"))
RISK_PCT = float(os.environ.get("XT_RUNNER_RISK", "1.0"))
MAX_POSITIONS = int(os.environ.get("XT_RUNNER_MAX_POS", "1"))
MAX_DAILY_LOSS_PCT = float(os.environ.get("XT_RUNNER_MAX_DAILY_LOSS", "3.0"))
SL_BUFFER_PCT = float(os.environ.get("XT_RUNNER_SL_BUFFER", "0.8"))

CYCLE_INTERVAL_SEC = int(os.environ.get("XT_RUNNER_INTERVAL", "120"))
MAX_CYCLES = int(os.environ.get("XT_RUNNER_MAX_CYCLES", "0"))
TIMEOUT_HOURS = float(os.environ.get("XT_RUNNER_TIMEOUT_HOURS", "4"))
STOP_FILE = "STOP_TRADING"

# ═══════════════════════════════════════════════════════════
# DETECTION
# ═══════════════════════════════════════════════════════════

def _c(c, idx, key):
    if isinstance(c, dict): return float(c.get(key, 0))
    if isinstance(c, (list, tuple)) and len(c) >= 5: return float(c[idx])
    return float(getattr(c, key, 0))


def _close(c): return _c(c, 4, "close")
def _high(c): return _c(c, 2, "high")
def _low(c): return _c(c, 3, "low")
def _open(c): return _c(c, 1, "open")
def _volume(c):
    """Return volume from any candle format (dict, list, object)."""
    if isinstance(c, dict):
        return float(c.get("volume", 0) or 0)
    if isinstance(c, (list, tuple)) and len(c) >= 6:
        return float(c[5])
    return float(getattr(c, "volume", 0) or 0)


def ema(values, period):
    if len(values) < period: return None
    k = 2.0 / (period + 1)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e


def btc_direction(candles):
    if not candles or len(candles) < 60: return "UNKNOWN"
    closes = [_close(c) for c in candles]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    if not e20 or not e50: return "UNKNOWN"
    diff = (e20 - e50) / e50 * 100
    if diff > 0.5: return "UP"
    if diff < -0.5: return "DOWN"
    return "FLAT"


def compute_channel(candles, period=30):
    if not candles or len(candles) < period + 1: return None
    closed = candles[:-1]
    if len(closed) < period: return None
    window = closed[-period:]
    highs = [_high(c) for c in window]
    lows = [_low(c) for c in window]
    upper, lower = max(highs), min(lows)
    mid = (upper + lower) / 2
    width = (upper - lower) / mid * 100 if mid > 0 else 0
    return {"upper": upper, "lower": lower, "mid": mid, "width_pct": width}


def candle_sig(candles):
    if not candles or len(candles) < 3: return None
    closed = candles[:-1]
    last = closed[-1]
    o, h, l, c = _open(last), _high(last), _low(last), _close(last)
    rng = h - l if h > l else 1e-9
    return {
        "bullish": c > o,
        "upper_wick_pct": (h - max(o, c)) / rng * 100,
        "lower_wick_pct": (min(o, c) - l) / rng * 100,
    }


def to_futures_symbol(spot_sym):
    """Convert FETUSDT -> fet_usdt for XT futures API."""
    s = spot_sym.upper()
    if s.endswith("USDT"):
        return s[:-4].lower() + "_usdt"
    return spot_sym.lower()

def candle_sig_with_volume(candles, window=10, min_ratio=1.2):
    """Candle signature with volume confirmation (last closed candle)."""
    if not candles or len(candles) < window + 2:
        return None

    closed = candles[:-1]
    if len(closed) < window + 1:
        return None

    last = closed[-1]
    o, h, l, c = _open(last), _high(last), _low(last), _close(last)
    rng = h - l if h > l else 1e-9

    # Previous N candles (excluding pullback candle)
    prev = closed[-(window + 1):-1]
    prev_vols = [_volume(pc) for pc in prev if _volume(pc) > 0]
    avg_vol = sum(prev_vols) / len(prev_vols) if prev_vols else 0
    last_vol = _volume(last)
    vol_ratio = last_vol / avg_vol if avg_vol > 0 else 0

    return {
        "bullish": c > o,
        "upper_wick_pct": (h - max(o, c)) / rng * 100,
        "lower_wick_pct": (min(o, c) - l) / rng * 100,
        "volume_ratio": round(vol_ratio, 2),
        "volume_confirmed": vol_ratio >= (min_ratio - 0.005),
    }


def bullish_pullback(sig):
    return sig and sig["lower_wick_pct"] >= 30 and sig.get("volume_confirmed", False)


def bearish_pullback(sig):
    return sig and sig["upper_wick_pct"] >= 30 and sig.get("volume_confirmed", False)


# ═══════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════

class Runner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.wrapper = XTFuturesExchange(
            dry_run=dry_run,
            extra_skip=["btc_usdt", "eth_usdt"]  # فقط برای skip_symbols داخلی
        )
        self.spot = XTExchange(timeout=10)
        self.state_file = (
            "data/futures_runner_state_dry.json" if dry_run
            else "data/futures_runner_state_live.json"
        )
        self.state = self._load_state()
        self.cycle_count = 0
        self._positions_cache = None
        self._positions_cache_cycle = None

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Runner] state load error: {e}")
        return {
            "started_at": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "daily_start_equity": None,
            "active_positions": {},
            "closed_positions": [],
        }

    def _save_state(self):
        self.state["last_cycle"] = datetime.now().isoformat()
        os.makedirs("data", exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def _rollover(self):
        today = date.today().isoformat()
        if self.state.get("date") != today:
            print(f"[Runner] new day {today}")
            self.state["date"] = today
            self.state["daily_start_equity"] = None
            self.state["closed_positions"] = []

    def _notify(self, msg):
        """Send Telegram message with retry + backoff. Env-configurable."""
        notifier = getattr(self.wrapper, "notifier", None)
        if not notifier:
            return

        max_retries = int(os.environ.get("TELEGRAM_MAX_RETRIES", "2"))
        base_delay  = float(os.environ.get("TELEGRAM_RETRY_DELAY", "1.5"))

        for attempt in range(max_retries + 1):
            try:
                notifier.send_message(msg)
                if attempt > 0:
                    print(f"[Telegram] delivered on attempt {attempt + 1}")
                return
            except Exception as e:
                if attempt < max_retries:
                    delay = base_delay * (attempt + 1)
                    print(f"[Telegram] attempt {attempt + 1}/{max_retries + 1} failed: "
                          f"{type(e).__name__}: {str(e)[:80]} — retry in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    print(f"[Telegram] all {max_retries + 1} attempts failed: "
                          f"{type(e).__name__}: {str(e)[:80]}")

    def _check_stop(self):
        if os.path.exists(STOP_FILE):
            return True, f"STOP file exists"
        return False, "OK"

    def _check_daily_loss(self):
        bal = self.wrapper.get_balance()
        if not bal: return True, "no balance"
        equity = bal["equity"]

        # DRY: add virtual PnL from state
        dry_pnl = 0
        if self.dry_run:
            for sym, info in self.state["active_positions"].items():
                price = self.wrapper._get_price(sym)
                if not price: continue
                size = info.get("size", 0)
                entry = info.get("entry", 0)
                csize = self.wrapper.get_contract_size(sym) or 1
                if info["side"] == "LONG":
                    dry_pnl += (price - entry) * size * csize
                else:
                    dry_pnl += (entry - price) * size * csize
            equity += dry_pnl
        if self.state.get("daily_start_equity") is None:
            self.state["daily_start_equity"] = equity
            return True, f"start equity ${equity:.2f}"
        start = self.state["daily_start_equity"]
        pnl_pct = (equity - start) / start * 100 if start > 0 else 0
        if pnl_pct <= -MAX_DAILY_LOSS_PCT:
            return False, f"daily loss {pnl_pct:.2f}%"
        return True, f"daily pnl {pnl_pct:+.2f}%"

    def _live_positions(self, refresh=False):
        """Return live positions with per-cycle cache to avoid rate limits."""
        if not refresh and self._positions_cache_cycle == self.cycle_count:
            return self._positions_cache
        
        all_live = {}
        for p in self.wrapper.get_user_positions():
            sym = p.get("symbol", "").lower()
            if float(p.get("positionSize", 0)) > 0:
                all_live[sym] = p
        
        self._positions_cache = None
        self._positions_cache_cycle = None
        self._last_signaled_syms = set()        # ← جدید
        self._last_signal_alert_cycle = 0       # ← جدید
        return all_live

    def _sync_state(self):
        """Remove state entries whose positions no longer exist (LIVE only)."""
        if self.dry_run:
            return   # DRY mode: state is virtual, don't sync
        all_live = self._live_positions(refresh=True)
        removed = []
        for sym in list(self.state["active_positions"].keys()):
            if sym not in all_live:
                removed.append(sym)
                del self.state["active_positions"][sym]
        if removed:
            print(f"[Sync] Removed (closed externally): {removed}")
            self._save_state()

    def _runner_position_count(self):
        """Count only runner-owned positions."""
        return len(self.state["active_positions"])

    def _monitor(self):
        live = self._live_positions()
        closed = []
        for sym, info in list(self.state["active_positions"].items()):
            price = self.wrapper._get_price(sym)
            if not price:
                print(f"  [Monitor] {sym} price unavailable")
                continue

            side = info["side"]
            initial = info.get("initial_entry", info["entry"])
            avg_count = info.get("avg_count", 0)

            # ─── Hard SL check ───
            if side == "LONG":
                hard_sl = initial * (1 - HARD_SL_PCT / 100)
                tp = info["tp"]
                hit_sl = price <= hard_sl
                hit_tp = price >= tp
            else:  # SHORT
                hard_sl = initial * (1 + HARD_SL_PCT / 100)
                tp = info["tp"]
                hit_sl = price >= hard_sl
                hit_tp = price <= tp

            # PnL for display
            pnl_pct = ((price - initial) / initial * 100) if side == "LONG" else ((initial - price) / initial * 100)

            print(f"  [Monitor] {sym} {side} price={price:.6g} "
                  f"PnL={pnl_pct:+.2f}% avg={avg_count}/{len(AVG_LEVELS_PCT)} "
                  f"SL_dist={abs(price-hard_sl)/hard_sl*100:.2f}% "
                  f"TP_dist={abs(price-tp)/tp*100:.2f}%")

            if hit_sl:
                closed.append((sym, "HARD_SL", price))
                continue
            if hit_tp:
                closed.append((sym, "TP", price))
                continue

            # ─── Averaging (only in LIVE, or simulate in DRY) ───
            if AVG_ENABLED and avg_count < len(AVG_LEVELS_PCT):
                next_level_pct = AVG_LEVELS_PCT[avg_count]
                if side == "LONG":
                    trigger = initial * (1 - next_level_pct / 100)
                    should_avg = price <= trigger
                else:
                    trigger = initial * (1 + next_level_pct / 100)
                    should_avg = price >= trigger

                if should_avg:
                    self._add_average(sym, info, avg_count, price)

            # ─── Remove averages at BE ───
            if REMOVE_AVG_AT_BE and avg_count > 0:
                if side == "LONG":
                    at_be = price >= initial
                else:
                    at_be = price <= initial
                if at_be:
                    self._remove_averages(sym, info, price)

            # ─── Trailing stop ───
            if TRAILING_ENABLED:
                self._update_trailing(info, price)

            # ─── Partial TP ───
            self._check_partial_tp(sym, info, price)

            # ─── Safety timeout (for DRY) ───
            if self.dry_run:
                opened = datetime.fromisoformat(info["opened_at"])
                if (datetime.now() - opened).total_seconds() > TIMEOUT_HOURS * 3600:
                    closed.append((sym, "TIMEOUT", price))

        # ─── Process closed positions ───
        for sym, reason, price in closed:
            info = self.state["active_positions"].pop(sym)
            entry = info.get("initial_entry", info["entry"])
            size = info.get("size", 0)
            side = info["side"]
            csize = self.wrapper.get_contract_size(sym) or 1

            # PnL for remaining position
            if side == "LONG":
                remaining_pnl = (price - entry) * size * csize
            else:
                remaining_pnl = (entry - price) * size * csize

            # Total = partial + remaining
            partial_pnl = info.get("partial_pnl_usdt", 0.0)
            total_pnl = partial_pnl + remaining_pnl

            self.state.setdefault("closed_positions", []).append({
                "symbol": sym, "side": side, "entry": entry,
                "exit_price": price, "reason": reason,
                "pnl_usdt": total_pnl,
                "partial_pnl_usdt": partial_pnl,
                "remaining_pnl_usdt": remaining_pnl,
                "closed_at": datetime.now().isoformat(),
            })
            mode = "DRY" if self.dry_run else "LIVE"
            print(f"  [{mode}] CLOSED {sym} {side} reason={reason} "
                  f"PnL={total_pnl:+.4f}$ "
                  f"(partial={partial_pnl:+.4f} + remaining={remaining_pnl:+.4f})")
            self._notify(
                f"🔴 {mode} CLOSED {sym.upper()} {side}\n"
                f"Reason: {reason} | PnL: {total_pnl:+.4f}$\n"
                f"Partial: {partial_pnl:+.4f}$ | Remaining: {remaining_pnl:+.4f}$"
            )

    def _add_average(self, sym, info, level_idx, price):
        """Add an averaging position, but only if BTC hasn't turned against us."""
        side = info["side"]

        # ─── BTC re-check: don't add to a losing position if BTC confirms against us
        try:
            btc_candles = self.spot.get_historical_candles("BTCUSDT", TIMEFRAME, limit=100)
            btc_now = btc_direction(btc_candles)
        except Exception as e:
            print(f"  [AVG] BTC check failed: {e}, skipping")
            return
        if self.dry_run and os.environ.get("XT_RUNNER_DRY_BTC_OVERRIDE"):
            btc_now = os.environ.get("XT_RUNNER_DRY_BTC_OVERRIDE").upper()
            print(f"  [AVG] BTC check: {btc_now} (OVERRIDE)")
        

        if side == "LONG" and btc_now == "DOWN":
            print(f"  [AVG] SKIP {sym} level {level_idx+1}: BTC is DOWN, not adding to LONG")
            self._notify(
                f"⚠️ AVG SKIP {sym.upper()} LONG level {level_idx+1}\n"
                f"Reason: BTC turned DOWN"
            )
            return
        if side == "SHORT" and btc_now == "UP":
            print(f"  [AVG] SKIP {sym} level {level_idx+1}: BTC is UP, not adding to SHORT")
            self._notify(
                f"⚠️ AVG SKIP {sym.upper()} SHORT level {level_idx+1}\n"
                f"Reason: BTC turned UP"
            )
            return

        add_size = int(info["initial_size"] * AVG_SIZE_MULT[level_idx])
        if add_size <= 0:
            return

        order_side = "SELL" if side == "SHORT" else "BUY"
        mode = "DRY" if self.dry_run else "LIVE"

        print(f"\n  [AVG] {mode} {side} {sym} +{add_size} @ level {level_idx+1}")
        print(f"        price={price:.6g} (level -{AVG_LEVELS_PCT[level_idx]}% from initial)")

        ok, resp = self.wrapper.place_order(
            symbol=sym, side=order_side, position_side=side,
            contracts=add_size, leverage=LEVERAGE,
        )

        if not ok or (isinstance(resp, dict) and resp.get("returnCode") not in (0, None)):
            print(f"  [AVG] FAILED: {resp}")
            return

        info["avg_count"] = level_idx + 1
        info["size"] = info["size"] + add_size
        info.setdefault("avg_entries", []).append({
            "price": price, "size": add_size, "at": datetime.now().isoformat()
        })
        total = info["size"]
        weighted = (info["entry"] * info["initial_size"] + price * add_size) / total if total > 0 else info["entry"]
        info["entry"] = weighted
        self._save_state()

        self._notify(
            f"➕ {mode} AVG {level_idx+1} {sym.upper()} {side}\n"
            f"Added: {add_size} @ {price:.6g}\n"
            f"Total: {total} contracts (weighted {weighted:.6g})"
        )

    def _remove_averages(self, sym, info, price):
        """Close avg positions when price returns to BE."""
        avg_count = info.get("avg_count", 0)
        if avg_count == 0:
            return

        side = info["side"]
        # Close quantity = total - initial_size
        avg_size_total = info["size"] - info["initial_size"]
        if avg_size_total <= 0:
            return

        order_side = "BUY" if side == "SHORT" else "SELL"  # opposite direction to close
        mode = "DRY" if self.dry_run else "LIVE"

        print(f"\n  [REMOVE_AVG] {mode} {side} {sym} close {avg_size_total} @ {price:.6g}")

        ok, resp = self.wrapper.place_order(
            symbol=sym, side=order_side, position_side=side,
            contracts=avg_size_total, leverage=LEVERAGE,
        )

        if not ok or (isinstance(resp, dict) and resp.get("returnCode") not in (0, None)):
            print(f"  [REMOVE_AVG] FAILED: {resp}")
            return

        info["size"] = info["initial_size"]
        info["entry"] = info["initial_entry"]
        info["avg_count"] = 0
        info["avg_entries"] = []
        self._save_state()

        self._notify(
            f"➖ {mode} REMOVED AVERAGES {sym.upper()} {side}\n"
            f"Closed: {avg_size_total} contracts @ {price:.6g}\n"
            f"Back to {info['size']} contracts at {info['initial_entry']:.6g}"
        )

    def _update_trailing(self, info, price):
        """Update trailing SL based on current price."""
        side = info["side"]
        initial = info.get("initial_entry", info["entry"])

        if side == "LONG":
            if price < initial * (1 + TRAILING_START_PCT / 100):
                return
            new_sl = price * (1 - TRAILING_DISTANCE_PCT / 100)
            if new_sl > info.get("trailing_sl", 0):
                info["trailing_sl"] = new_sl
        else:  # SHORT
            if price > initial * (1 - TRAILING_START_PCT / 100):
                return
            new_sl = price * (1 + TRAILING_DISTANCE_PCT / 100)
            if info.get("trailing_sl", float("inf")) == float("inf") or new_sl < info.get("trailing_sl", float("inf")):
                info["trailing_sl"] = new_sl

    def _check_partial_tp(self, sym, info, price):
        """Take partial profit at 50% of TP distance (once, no averages active)."""
        if not PARTIAL_TP_ENABLED:
            return
        if info.get("partial_taken"):
            return
        if info.get("avg_count", 0) > 0:
            return

        side = info["side"]
        entry = info["initial_entry"]
        tp = info["tp"]
        size = info["size"]

        if size <= 1:
            return

        if side == "LONG":
            half_tp = entry + (tp - entry) * PARTIAL_TP_AT_PCT / 100
            hit = price >= half_tp
        else:
            half_tp = entry - (entry - tp) * PARTIAL_TP_AT_PCT / 100
            hit = price <= half_tp

        if not hit:
            return

        close_size = int(size * PARTIAL_TP_FRACTION)
        if close_size <= 0:
            return

        order_side = "BUY" if side == "SHORT" else "SELL"
        mode = "DRY" if self.dry_run else "LIVE"

        print(f"\n  [PARTIAL_TP] {mode} {side} {sym} close {close_size}/{size} @ {price:.6g}")
        print(f"        half_tp={half_tp:.6g} ({PARTIAL_TP_AT_PCT}% of TP distance)")

        ok, resp = self.wrapper.place_order(
            symbol=sym, side=order_side, position_side=side,
            contracts=close_size, leverage=LEVERAGE,
        )

        if not ok or (isinstance(resp, dict) and resp.get("returnCode") not in (0, None)):
            print(f"  [PARTIAL_TP] FAILED: {resp}")
            return

        info["size"] = size - close_size
        info["partial_taken"] = True

        # ─── Track partial PnL ───
        csize = self.wrapper.get_contract_size(sym) or 1
        if side == "LONG":
            partial_pnl = (price - entry) * close_size * csize
        else:
            partial_pnl = (entry - price) * close_size * csize
        info["partial_pnl_usdt"] = info.get("partial_pnl_usdt", 0.0) + partial_pnl

        self._save_state()

        self._notify(
            f"💰 {mode} PARTIAL TP {sym.upper()} {side}\n"
            f"Closed: {close_size}/{size} @ {price:.6g}\n"
            f"PnL: {partial_pnl:+.4f}$\n"
            f"Remaining: {info['size']} contracts\n"
            f"Half-TP: {half_tp:.6g} ({PARTIAL_TP_AT_PCT}%)"
        )

    def _detect(self, btc_dir):
        setups = []
        for sym in SYMBOLS:
            sym_l = to_futures_symbol(sym)
            if sym_l in self.wrapper.skip_symbols: continue
            if sym_l in self.state["active_positions"]: continue  # ← NEW: skip already open
            try:
                candles = self.spot.get_historical_candles(sym, TIMEFRAME, limit=CHANNEL_PERIOD + 20)
            except Exception as e:
                continue
            if not candles or len(candles) < CHANNEL_PERIOD + 5: continue
            ch = compute_channel(candles, CHANNEL_PERIOD)
            if not ch: continue
            if ch["width_pct"] < MIN_WIDTH_PCT or ch["width_pct"] > MAX_WIDTH_PCT: continue
            price = _close(candles[-1])
            pos_pct = (price - ch["lower"]) / (ch["upper"] - ch["lower"]) * 100
            sig = candle_sig_with_volume(candles, window=10)  # ← به‌جای candle_sig
            
            side = None
            if btc_dir == "UP" and pos_pct <= LONG_MAX_POS and bullish_pullback(sig):
                side = "LONG"
            elif ALLOW_SHORT and btc_dir == "DOWN" and pos_pct >= SHORT_MIN_POS and bearish_pullback(sig):
                side = "SHORT"
            elif btc_dir == "FLAT":
                if pos_pct <= LONG_MAX_POS and bullish_pullback(sig):
                    side = "LONG"
                elif ALLOW_SHORT and pos_pct >= SHORT_MIN_POS and bearish_pullback(sig):
                    side = "SHORT"
            
            if side:
                if side == "SHORT":
                    sl = ch["upper"] * (1 + SL_BUFFER_PCT / 100)
                    tp = ch["mid"]
                else:
                    sl = ch["lower"] * (1 - SL_BUFFER_PCT / 100)
                    tp = ch["mid"]
                setups.append({
                    "symbol": sym_l, "side": side, "pos_pct": pos_pct,
                    "channel": ch, "sl": sl, "tp": tp, "price": price,
                    "volume_ratio": sig.get("volume_ratio", 0),
                })
        
        # Sort by edge extremity
        setups.sort(key=lambda s: min(s["pos_pct"], 100 - s["pos_pct"]))
        return setups

    def _execute(self, setup):
        sym = setup["symbol"]
        side = setup["side"]
        if sym in self.state["active_positions"]:
            print(f"[Exec] {sym} already in state")
            return False

        sizing = self.wrapper.calculate_contracts(sym, risk_pct=RISK_PCT, leverage=LEVERAGE)
        if "error" in sizing:
            print(f"[Exec] sizing error: {sizing['error']}")
            return False
        contracts = sizing["contracts"]
        if contracts <= 0:
            print(f"[Exec] contracts=0, skip")
            return False

        order_side = "SELL" if side == "SHORT" else "BUY"
        mode = "DRY" if self.dry_run else "LIVE"

        print(f"\n[Exec] {mode} {side} {sym} {contracts} @ {LEVERAGE}x")
        print(f"       Entry~{sizing['price']:.6g} "
              f"Avg1@{AVG_LEVELS_PCT[0]}% Avg2@{AVG_LEVELS_PCT[1]}% "
              f"HardSL@{HARD_SL_PCT}%")

        # Place order WITHOUT SL/TP (TP will be checked in monitor)
        ok, resp = self.wrapper.place_order(
            symbol=sym, side=order_side, position_side=side,
            contracts=contracts, leverage=LEVERAGE,
            sl_price=None, tp_price=None,
        )

        if not ok or (isinstance(resp, dict) and resp.get("returnCode") not in (0, None)):
            print(f"[Exec] FAILED: {resp}")
            self._notify(f"❌ {mode} FAILED {side} {sym}: {str(resp)[:100]}")
            return False

        self.state["active_positions"][sym] = {
            "side": side,
            "size": contracts,
            "initial_size": contracts,
            "initial_entry": sizing["price"],
            "entry": sizing["price"],
            "tp": setup["tp"],
            "avg_count": 0,
            "avg_entries": [],
            "partial_taken": False,
            "partial_pnl_usdt": 0.0,        # ← جدید
            "opened_at": datetime.now().isoformat(),
        }
        self._save_state()

        self._notify(
            f"🟢 {mode} {side} OPEN\n"
            f"{sym.upper()} {contracts} contracts @ {LEVERAGE}x\n"
            f"Entry: {sizing['price']:.6g}\n"
            f"TP: {setup['tp']:.6g} | HardSL: {HARD_SL_PCT}%"
        )
        return True

    def cycle(self):
        self.cycle_count += 1
        self._rollover()
        
        print(f"\n{'='*70}")
        print(f"[Cycle {self.cycle_count}] {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        
        stop, reason = self._check_stop()
        if stop:
            print(f"[STOP] {reason}")
            return False
        
        ok_loss, loss_msg = self._check_daily_loss()
        print(f"[Risk] {loss_msg}")
        if not ok_loss:
            self._notify(f"⛔ DAILY LOSS: {loss_msg}")
            return False
        
        self._monitor()
        
        try:
            btc_candles = self.spot.get_historical_candles("BTCUSDT", TIMEFRAME, limit=100)
            btc_dir = btc_direction(btc_candles)
            self.state["last_btc_dir"] = btc_dir
        except Exception as e:
            print(f"[BTC] fetch failed: {e}")
            btc_dir = self.state.get("last_btc_dir", "UNKNOWN")
            if btc_dir == "UNKNOWN":
                print("[BTC] no cached direction, skipping cycle")
                self._save_state()
                return True
        print(f"[BTC] {btc_dir}")
        
        self._sync_state()   # پاکسازی state از پوزیشن‌های بسته‌شده خارجی
        
        runner_count = self._runner_position_count()
        all_live = self._live_positions()
        manual_count = len(all_live) - runner_count
        
        self._print_positions_report()
        
        setups = self._detect(btc_dir)
        print(f"[Detect] {len(setups)} setups")
        
        if setups:
            # ─── Show ALL candidates (configurable limit) ───
            for i, s in enumerate(setups[:MAX_SIGNALS_DISPLAY], 1):
                print(f"  {i:2d}. {s['side']:5s} {s['symbol']:12s} "
                      f"pos={s['pos_pct']:5.1f}% vol={s['volume_ratio']:.2f}x "
                      f"price={s['price']:.6g} SL={s['sl']:.6g} TP={s['tp']:.6g}")

            if runner_count >= MAX_POSITIONS:
                # ═══ SIGNAL MODE: max positions reached ═══
                pending = setups  # all are new (filtered in _detect)
                print(f"\n  📡 SIGNAL MODE ({runner_count}/{MAX_POSITIONS} filled)")
                print(f"     {len(pending)} pending setup(s) - NOT executed:")
                for s in pending[:MAX_SIGNALS_DISPLAY]:
                    print(f"     {s['side']:5s} {s['symbol']:12s} "
                          f"pos={s['pos_pct']:3.0f}% vol={s['volume_ratio']:.1f}x "
                          f"entry~{s['price']:.6g} "
                          f"SL={s['sl']:.6g} TP={s['tp']:.6g}")

                # ─── Throttled Telegram alert ───
                pending_syms = {s["symbol"] for s in pending}
                changed = pending_syms != self._last_signaled_syms
                cycles_since = self.cycle_count - self._last_signal_alert_cycle

                if pending and (changed or cycles_since >= SIGNAL_ALERT_EVERY):
                    self._last_signaled_syms = pending_syms
                    self._last_signal_alert_cycle = self.cycle_count

                    lines = [f"📡 SIGNAL ALERT ({runner_count}/{MAX_POSITIONS} filled)"]
                    for s in pending[:5]:
                        lines.append(
                            f"\n{s['side']} {s['symbol'].upper()}\n"
                            f"  pos={s['pos_pct']:.0f}% vol={s['volume_ratio']:.1f}x\n"
                            f"  entry~{s['price']:.6g}\n"
                            f"  SL={s['sl']:.6g} TP={s['tp']:.6g}"
                        )
                    self._notify("\n".join(lines))
                    print(f"  [Telegram] Alert sent ({len(pending)} setups)")
            else:
                # ═══ EXECUTION MODE: slots available ═══
                for s in setups[:MAX_POSITIONS - runner_count]:
                    if self._execute(s):
                        break
        self._save_state()
        return True   
                
    def _print_positions_report(self):
        """Show protected, runner, and manual positions clearly."""
        all_live = self._live_positions()
        runner_syms = set(self.state["active_positions"].keys())
        manual_syms = set(all_live.keys()) - runner_syms
        protected = set(self.wrapper.skip_symbols)

        print(f"\n  +- POSITIONS ---------------------------------- +")

        # Protected (BTC/ETH on XT)
        for sym in sorted(protected):
            if sym in all_live:
                p = all_live[sym]
                print(f"  | [LOCK]  {sym:12s} {p.get('positionSide', '?'):5s} "
                      f"sz={p.get('positionSize', '0'):>8} entry={p.get('entryPrice', '?')}")

        # Runner positions (from state - virtual in DRY, real in LIVE)
        for sym in sorted(runner_syms):
            info = self.state["active_positions"][sym]
            marker = "VIRTUAL" if self.dry_run else "REAL"
            avg_count = info.get("avg_count", 0)
            avg_str = f" avg={avg_count}/{len(AVG_LEVELS_PCT)}" if avg_count > 0 else ""
            entry = info.get('entry', 0)
            try:
                entry_str = f"{entry:.6g}"
            except (ValueError, TypeError):
                entry_str = str(entry)
            print(f"  | [ROBOT] {sym:12s} {info['side']:5s} "
                  f"sz={info.get('size', '?'):>4} entry={entry_str}"
                  f"{avg_str}  ({marker})")

        # Other manual (not protected, not runner)
        for sym in sorted(manual_syms - protected):
            p = all_live[sym]
            print(f"  | [HUMAN] {sym:12s} {p.get('positionSide', '?'):5s} "
                  f"sz={p.get('positionSize', '0'):>8} entry={p.get('entryPrice', '?')}")

        print(f"  +------------------------------------------------+")
        total_display = len(all_live) + len([s for s in runner_syms if s not in all_live])
        print(f"  Summary: runner={len(runner_syms)} | manual={len(manual_syms)} | total={total_display}")

    def run(self):
        mode = "DRY RUN (no real orders)" if self.dry_run else "LIVE TRADING"
        print(f"\n{'#'*70}")
        print(f"# Futures Strategy Runner")
        print(f"# Mode: {mode}")
        print(f"# Leverage: {LEVERAGE}x | Risk: {RISK_PCT}% | Max pos: {MAX_POSITIONS}")
        print(f"# SHORT entries: {'ON' if ALLOW_SHORT else 'OFF (LONG-only mode)'}")
        print(f"# Daily loss limit: {MAX_DAILY_LOSS_PCT}%")
        print(f"# Interval: {CYCLE_INTERVAL_SEC}s | Max cycles: {MAX_CYCLES or 'infinite'}")
        print(f"# STOP file: {STOP_FILE} (touch to stop)")
        print(f"{'#'*70}")

        if not self.dry_run:
            print("\nLIVE MODE - REAL MONEY WILL BE TRADED")
            r = input("Type LIVE to confirm: ").strip()
            if r != "LIVE":
                print("Aborted.")
                return

        self._notify(f"Runner started ({mode})")

        try:
            while True:
                try:
                    if not self.cycle():
                        break
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"[Cycle] ERROR: {e}")
                    import traceback
                    traceback.print_exc()

                if MAX_CYCLES > 0 and self.cycle_count >= MAX_CYCLES:
                    print(f"[Runner] max cycles reached")
                    break

                time.sleep(CYCLE_INTERVAL_SEC)
        except KeyboardInterrupt:
            print("\n[Runner] Interrupted")
        finally:
            self._save_state()
            self._notify(f"Runner stopped after {self.cycle_count} cycles")


if __name__ == "__main__":
    live = os.environ.get("XT_FUTURES_LIVE", "0") == "1"
    Runner(dry_run=not live).run()
