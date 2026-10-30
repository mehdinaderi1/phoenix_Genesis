"""
tools/spot_runner.py — Spot DCA + Buy-the-Dip Runner (DRY RUN by default)

Strategy:
  - Reference high: highest high of last 42 x 4H candles (7 days)
  - Ladder: -10%, -15%, -20%, -25%, -30% from ref high
  - Each step = 20% of allocation (fixed weight, no leverage)
  - TP1: +20% from avg entry (sell 50%)
  - TP2: +40% from avg entry (sell remaining)
  - Timeout: 60 days per position

Usage:
    python tools/spot_runner.py
    python tools/spot_runner.py --live   # (requires XT_FUTURES_LIVE=1)

NOTE: DRY RUN only writes state; no orders are placed.
"""
import os, sys, time, json
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange

# ─── Config ───
SYMBOLS = [
    "ETHUSDT","SOLUSDT","ARBUSDT","OPUSDT","DOGEUSDT","PEPEUSDT",
    "AAVEUSDT","INJUSDT","FETUSDT","WLDUSDT","ZECUSDT","XMRUSDT",
    "XRPUSDT","DASHUSDT",
]
TIMEFRAME          = "4H"
REF_HIGH_LOOKBACK  = 42
LADDER_PCT         = [10, 15, 20, 25, 30]
LADDER_WEIGHT      = [0.2, 0.2, 0.2, 0.2, 0.2]
TP1_PCT            = 20
TP2_PCT            = 40
TP1_FRACTION       = 0.5
TIMEOUT_DAYS       = 60
MAX_CONCURRENT     = 5      # max symbols open at once
CYCLE_INTERVAL_SEC = 300    # 5 min (spot doesn't need 60s)
TIMEOUT_HOURS      = 48     # runner auto-stop

STATE_FILE = "data/spot_runner_state_dry.json"
STOP_FILE  = "STOP_TRADING"
TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED", "0") == "1"


class SpotRunner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.spot = XTExchange(timeout=20)
        self.state = self._load_state()
        self.cycle_count = 0
        self._ref_highs = {}  # cache per symbol

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Spot] state load error: {e}")
        return {
            "started_at": datetime.now().isoformat(),
            "positions": {},        # symbol -> {levels_filled, avg_entry, size, tp1_taken, ...}
            "closed": [],
        }

    def _save_state(self):
        self.state["last_cycle"] = datetime.now().isoformat()
        os.makedirs("data", exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def _notify(self, msg):
        if not TELEGRAM_ENABLED:
            return
        try:
            from notifications.telegram_sender import TelegramSender
            TelegramSender().send_message(msg)
        except Exception as e:
            print(f"[Telegram] {e}")

    def _check_stop(self):
        if os.path.exists(STOP_FILE):
            return True
        return False

    def _get_ref_high(self, sym, candles):
        if len(candles) < REF_HIGH_LOOKBACK + 1:
            return None
        window = candles[-REF_HIGH_LOOKBACK - 1:-1]  # exclude forming candle
        return max(c["high"] for c in window)

    def _scan(self):
        """Scan all symbols; return list of (sym, candle, ref_high)."""
        results = []
        for sym in SYMBOLS:
            try:
                candles = self.spot.get_historical_candles(sym, TIMEFRAME, limit=60)
            except Exception as e:
                print(f"  [Scan] {sym}: fetch failed {type(e).__name__}")
                continue
            if not candles or len(candles) < REF_HIGH_LOOKBACK + 5:
                continue
            ref_high = self._get_ref_high(sym, candles)
            if ref_high:
                results.append((sym, candles[-1], ref_high))
            time.sleep(0.2)
        return results

    def _process_symbol(self, sym, last_candle, ref_high):
        """Check ladder / TP1 / TP2 for a symbol. Returns action string."""
        price_low  = last_candle["low"]
        price_high = last_candle["high"]
        price_close = last_candle["close"]

        pos = self.state["positions"].get(sym)

        # ─── No position yet: check ladder ───
        if pos is None:
            filled = 0
            total_size = 0.0
            total_cost = 0.0
            for lvl_idx, pct in enumerate(LADDER_PCT):
                trigger = ref_high * (1 - pct / 100)
                if price_low <= trigger:
                    w = LADDER_WEIGHT[lvl_idx]
                    total_size += w
                    total_cost += w * trigger
                    filled += 1
                else:
                    break
            if filled == 0:
                return None
            avg = total_cost / total_size
            self.state["positions"][sym] = {
                "levels_filled": filled,
                "avg_entry": avg,
                "size": total_size,
                "tp1_taken": False,
                "ref_high": ref_high,
                "opened_at": datetime.now().isoformat(),
            }
            self._save_state()
            self._notify(
                f"🟢 SPOT DCA {sym} — {filled} levels\n"
                f"avg_entry={avg:.6g}  size={total_size:.2f}"
            )
            return f"OPEN {filled} levels @ {avg:.6g}"

        # ─── Position exists: check TP1 / TP2 / ladder top-ups / timeout ───
        filled = pos["levels_filled"]
        avg = pos["avg_entry"]
        size = pos["size"]

        # Ladder top-ups (if price dropped further)
        while filled < len(LADDER_PCT):
            trigger = ref_high * (1 - LADDER_PCT[filled] / 100)
            if price_low <= trigger:
                w = LADDER_WEIGHT[filled]
                new_total = size + w
                new_cost = avg * size + w * trigger
                avg = new_cost / new_total
                size = new_total
                filled += 1
                pos["levels_filled"] = filled
                pos["avg_entry"] = avg
                pos["size"] = size
                self._save_state()
                self._notify(f"➕ SPOT DCA {sym} level {filled} @ {trigger:.6g}")
            else:
                break

        # TP1
        if not pos.get("tp1_taken"):
            tp1_price = avg * (1 + TP1_PCT / 100)
            if price_high >= tp1_price:
                sold = size * TP1_FRACTION
                self.state.setdefault("closed", []).append({
                    "symbol": sym, "reason": "TP1",
                    "avg_entry": avg, "exit_price": tp1_price,
                    "size": sold, "pnl_pct": TP1_PCT,
                    "closed_at": datetime.now().isoformat(),
                })
                pos["tp1_taken"] = True
                pos["size"] = size - sold
                self._save_state()
                self._notify(f"💰 SPOT TP1 {sym} @ {tp1_price:.6g} (+{TP1_PCT}%)")
                return f"TP1 @ {tp1_price:.6g}"

        # TP2 (remaining)
        tp2_price = avg * (1 + TP2_PCT / 100)
        if price_high >= tp2_price:
            self.state.setdefault("closed", []).append({
                "symbol": sym, "reason": "TP2",
                "avg_entry": avg, "exit_price": tp2_price,
                "size": pos["size"], "pnl_pct": TP2_PCT,
                "closed_at": datetime.now().isoformat(),
            })
            del self.state["positions"][sym]
            self._save_state()
            self._notify(f"💰 SPOT TP2 {sym} @ {tp2_price:.6g} (+{TP2_PCT}%)")
            return f"TP2 @ {tp2_price:.6g}"

        # Timeout
        opened = datetime.fromisoformat(pos["opened_at"])
        if (datetime.now() - opened).days > TIMEOUT_DAYS:
            self.state.setdefault("closed", []).append({
                "symbol": sym, "reason": "TIMEOUT",
                "avg_entry": avg, "exit_price": price_close,
                "size": pos["size"],
                "pnl_pct": (price_close - avg) / avg * 100,
                "closed_at": datetime.now().isoformat(),
            })
            del self.state["positions"][sym]
            self._save_state()
            self._notify(f"⏰ SPOT TIMEOUT {sym} @ {price_close:.6g}")
            return f"TIMEOUT @ {price_close:.6g}"

        return None

    def cycle(self):
        self.cycle_count += 1
        print(f"\n{'='*70}")
        print(f"[Spot Cycle {self.cycle_count}] {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")

        if self._check_stop():
            print("[STOP] STOP_TRADING file exists")
            return False

        # Show current positions
        print(f"\n  Active positions: {len(self.state['positions'])}")
        for sym, p in self.state["positions"].items():
            print(f"    {sym:12s} levels={p['levels_filled']}/5 "
                  f"avg={p['avg_entry']:.6g} size={p['size']:.2f} "
                  f"tp1={'Y' if p['tp1_taken'] else 'N'}")

        # Enforce max concurrent
        if len(self.state["positions"]) >= MAX_CONCURRENT:
            print(f"\n  [LIMIT] {MAX_CONCURRENT} concurrent positions — no new entries")
            return True

        # Scan + process
        print(f"\n  Scanning {len(SYMBOLS)} symbols...")
        results = self._scan()
        actions = []
        for sym, candle, ref_high in results:
            if len(self.state["positions"]) >= MAX_CONCURRENT and sym not in self.state["positions"]:
                continue
            act = self._process_symbol(sym, candle, ref_high)
            if act:
                actions.append(f"{sym}: {act}")

        if actions:
            print(f"\n  Actions: {len(actions)}")
            for a in actions:
                print(f"    {a}")
        else:
            print(f"  No actions this cycle")

        self._save_state()
        return True

    def run(self):
        mode = "DRY RUN" if self.dry_run else "LIVE"
        print(f"\n{'#'*70}")
        print(f"# Spot DCA Runner  ({mode})")
        print(f"# Symbols: {len(SYMBOLS)} | Ladder: {LADDER_PCT} | TP: +{TP1_PCT}%/+{TP2_PCT}%")
        print(f"# Interval: {CYCLE_INTERVAL_SEC}s | Max concurrent: {MAX_CONCURRENT}")
        print(f"# STOP file: {STOP_FILE}")
        print(f"{'#'*70}")

        self._notify(f"Spot Runner started ({mode})")

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
                time.sleep(CYCLE_INTERVAL_SEC)
        except KeyboardInterrupt:
            print("\n[Spot] Interrupted")
        finally:
            self._save_state()


if __name__ == "__main__":
    live = "--live" in sys.argv and os.environ.get("XT_FUTURES_LIVE") == "1"
    SpotRunner(dry_run=not live).run()