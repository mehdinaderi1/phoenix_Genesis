"""
tools/spot_runner.py — Spot DCA Runner (DRY RUN by default)
USDT-based: buys a fixed % of balance at each ladder step.
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
LADDER_PCT         = [10, 15, 20, 25, 30]  # درصد افت از سقف
BASE_ORDER_PCT     = 0.01   # ۱٪ از موجودی برای پله اول
MAX_SPOT_USAGE_PCT = 0.50  # حداکثر ۵۰٪ سرمایه برای اسپات
LADDER_MULTIPLIER  = [1, 2, 4, 8, 16]  # ضریب هر پله نسبت به پله اول
TP1_PCT            = 20
TP2_PCT            = 40
TP1_FRACTION       = 0.5
TIMEOUT_DAYS       = 60
MAX_CONCURRENT     = 8
CYCLE_INTERVAL_SEC = 300
STATE_FILE = "data/spot_runner_state_dry.json"
STOP_FILE  = "STOP_TRADING"
TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED", "0") == "1"


class SpotRunner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.spot = XTExchange(timeout=20)
        self.state = self._load_state()
        self.cycle_count = 0

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Spot] state load error: {e}")
        return {
            "started_at": datetime.now().isoformat(),
            "positions": {},
            "closed": [],
        }

    def _save_state(self):
        self.state["last_cycle"] = datetime.now().isoformat()
        os.makedirs("data", exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def _notify(self, msg):
        if not TELEGRAM_ENABLED: return
        try:
            from notifications.telegram_sender import TelegramSender
            TelegramSender().send_message(msg)
        except Exception as e:
            print(f"[Telegram] {e}")

    def _check_stop(self):
        return os.path.exists(STOP_FILE)

    def _get_balance(self):
        """دریافت موجودی: در DRY RUN ثابت ۲۰۰، در LIVE واقعی"""
        if self.dry_run:
            return 200.0  # سرمایه فرضی برای تست
        try:
            from tools.futures_wrapper_v2 import XTFuturesExchange
            wrapper = XTFuturesExchange(dry_run=False)
            bal = wrapper.get_balance()
            if bal and "equity" in bal:
                return float(bal["equity"])
            return 0.0
        except Exception as e:
            print(f"[Spot] Balance fetch error: {e}")
            return 0.0

    def _get_ref_high(self, candles):
        if len(candles) < REF_HIGH_LOOKBACK + 1: return None
        window = candles[-REF_HIGH_LOOKBACK - 1:-1]
        return max(c["high"] for c in window)

    def _scan(self):
        results = []
        for sym in SYMBOLS:
            try:
                candles = self.spot.get_historical_candles(sym, TIMEFRAME, limit=60)
            except Exception:
                continue
            if not candles or len(candles) < REF_HIGH_LOOKBACK + 5:
                continue
            ref_high = self._get_ref_high(candles)
            if ref_high:
                results.append((sym, candles[-1], ref_high))
            time.sleep(0.2)
        return results

    def _process_symbol(self, sym, last_candle, ref_high, balance):
        price_low  = last_candle["low"]
        price_high = last_candle["high"]
        price_close = last_candle["close"]

        pos = self.state["positions"].get(sym)

        # ─── No position yet: check ladder ───
        current_invested = sum(p.get('total_usdt', 0) for p in self.state["positions"].values())
        max_allowed = balance * MAX_SPOT_USAGE_PCT
        
        if current_invested >= max_allowed:
            return None 

        if pos is None:
            filled = 0
            total_usdt = 0.0
            base_amount = balance * BASE_ORDER_PCT
            for lvl_idx, pct in enumerate(LADDER_PCT):
                trigger = ref_high * (1 - pct / 100)
                if price_low <= trigger:
                    amount_usdt = base_amount * LADDER_MULTIPLIER[lvl_idx]
                    total_usdt += amount_usdt
                    filled += 1
                else:
                    break
            if filled == 0:
                return None
            self.state["positions"][sym] = {
                "levels_filled": filled,
                "total_usdt": total_usdt,
                "avg_entry": price_close, 
                "ref_high": ref_high,
                "opened_at": datetime.now().isoformat(),
            }
            self._save_state()
            self._notify(
                f"🟢 SPOT DCA {sym} — {filled} levels\n"
                f"total_usdt=${total_usdt:.2f}"
            )
            return f"OPEN {filled} levels @ ${total_usdt:.2f}"

        # ─── Position exists ───
        filled = pos["levels_filled"]
        total_usdt = pos["total_usdt"]
        avg = pos["avg_entry"]
        base_amount = balance * BASE_ORDER_PCT

        # Ladder top-ups
        while filled < len(LADDER_PCT):
            current_invested = sum(p.get('total_usdt', 0) for p in self.state["positions"].values())
            if current_invested >= max_allowed:
                break

            trigger = ref_high * (1 - LADDER_PCT[filled] / 100)
            if price_low <= trigger:
                amount_usdt = base_amount * LADDER_MULTIPLIER[filled]
                new_total = total_usdt + amount_usdt
                buy_price = trigger 
                new_avg = ((pos["avg_entry"] * total_usdt) + (buy_price * amount_usdt)) / new_total
                
                pos["avg_entry"] = new_avg
                pos["total_usdt"] = new_total
                pos["levels_filled"] = filled + 1
                
                filled += 1
                self._save_state()
                self._notify(f"➕ SPOT DCA {sym} level {filled} | +${amount_usdt:.2f}")
            else:
                break

        # TP1
        if not pos.get("tp1_taken"):
            tp1_price = avg * (1 + TP1_PCT / 100)
            if price_high >= tp1_price:
                sold_usdt = total_usdt * TP1_FRACTION
                self.state.setdefault("closed", []).append({
                    "symbol": sym, "reason": "TP1",
                    "avg_entry": avg, "exit_price": tp1_price,
                    "usdt": sold_usdt, "pnl_pct": TP1_PCT,
                    "closed_at": datetime.now().isoformat(),
                })
                pos["tp1_taken"] = True
                pos["total_usdt"] = total_usdt - sold_usdt
                self._save_state()
                self._notify(f"💰 SPOT TP1 {sym} @ {tp1_price:.6g} (+{TP1_PCT}%)")
                return f"TP1 @ {tp1_price:.6g}"

        # TP2
        tp2_price = avg * (1 + TP2_PCT / 100)
        if price_high >= tp2_price:
            self.state.setdefault("closed", []).append({
                "symbol": sym, "reason": "TP2",
                "avg_entry": avg, "exit_price": tp2_price,
                "usdt": total_usdt, "pnl_pct": TP2_PCT,
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
                "usdt": total_usdt,
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

        balance = self._get_balance()
        if balance <= 0:
            print("[Spot] No balance available")
            return True

        print(f"\n  Active positions: {len(self.state['positions'])}")
        for sym, p in self.state["positions"].items():
            print(f"    {sym:12s} levels={p['levels_filled']}/5 | value=${p['total_usdt']:.2f}")

        if len(self.state["positions"]) >= MAX_CONCURRENT:
            print(f"\n  [LIMIT] {MAX_CONCURRENT} concurrent positions — no new entries")
            return True

        print(f"\n  Scanning {len(SYMBOLS)} symbols...")
        results = self._scan()
        actions = []
        for sym, candle, ref_high in results:
            if len(self.state["positions"]) >= MAX_CONCURRENT and sym not in self.state["positions"]:
                continue
            act = self._process_symbol(sym, candle, ref_high, balance)
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
        print(f"# Base order: {BASE_ORDER_PCT*100}% of balance")
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