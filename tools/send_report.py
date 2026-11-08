"""
tools/send_report.py — Send a periodic status report to Telegram
"""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from notifications.telegram_sender import TelegramSender

FUTURES_STATE = "data/futures_runner_state_dry.json"
SPOT_STATE = "data/spot_runner_state_dry.json"
BTC_SYMBOL = "BTCUSDT"

def load_state(path):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: pass
    return {}

def main():
    spot = XTExchange(timeout=15)
    notifier = TelegramSender()
    
    # ─── 1. وضعیت بازار ───
    try:
        btc_c = spot.get_historical_candles(BTC_SYMBOL, "1H", limit=4)
        btc_price = btc_c[-1]["close"] if btc_c else 0
        change_3h = (btc_c[-1]["close"] - btc_c[0]["open"]) / btc_c[0]["open"] * 100 if btc_c else 0
        btc_trend = "🟢 UP" if change_3h > 0.5 else ("🔴 DOWN" if change_3h < -0.5 else "⚪ FLAT")
    except:
        btc_price, change_3h, btc_trend = 0, 0, "UNKNOWN"

    # ─── 2. وضعیت فیوچرز ───
    f_state = load_state(FUTURES_STATE)
    f_active = f_state.get("active_positions", {})
    f_closed = f_state.get("closed_positions", [])
    f_last_btc = f_state.get("last_btc_dir", "?")
    f_equity = f_state.get("daily_start_equity", 0)
    
    # ─── 3. وضعیت اسپات ───
    s_state = load_state(SPOT_STATE)
    s_active = s_state.get("positions", {})
    
    # ─── ساخت پیام ───
    lines = [
        f"📊 **Phoenix Status Report**",
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"📈 **بازار**",
        f"BTC: ${btc_price:,.0f} ({change_3h:+.2f}% در ۳ ساعت)",
        f"روند: {btc_trend}",
        f"",
        f"🤖 **فیوچرز (LONG-only)**",
        f"موجودی: ${f_equity:.2f}",
        f"پوزیشن‌های باز: {len(f_active)}",
    ]
    if s_active:
        total_invested = 0.0
        total_pnl_usdt = 0.0
        total_pnl_pct = 0.0
        count = 0
        
        for sym, info in s_active.items():
            levels = info.get('levels_filled', 1)
            value = info.get('total_usdt', 0.0)
            avg_entry = info.get('avg_entry', 0)
            total_invested += value
            
            try:
                price_data = spot.get_historical_candles(sym, "1H", limit=1)
                current_price = price_data[0]["close"] if price_data else avg_entry
                
                # محاسبه سود/ضرر به درصد و دلار
                pnl_pct = (current_price - avg_entry) / avg_entry * 100 if avg_entry > 0 else 0
                pnl_usdt = value * (pnl_pct / 100)
                
                total_pnl_usdt += pnl_usdt
                total_pnl_pct += pnl_pct
                count += 1
                
                # نمایش هر دو (درصد و دلار)
                lines.append(f"  • {sym.upper()} پله {levels}/5 | ارزش: ${value:.2f} | PnL: {pnl_pct:+.1f}% (${pnl_usdt:+.2f})")
            except:
                lines.append(f"  • {sym.upper()} پله {levels}/5 | ارزش: ${value:.2f} | PnL: ?")
        
        lines.append(f"  ─────────────────")
        lines.append(f"  💰 مجموع سرمایه درگیر: ${total_invested:.2f}")
        
        if count > 0:
            avg_pnl = total_pnl_pct / count
            lines.append(f"  📊 میانگین سود/ضرر کل: {avg_pnl:+.1f}% (${total_pnl_usdt:+.2f})")
    else:
        lines.append("  (بدون پوزیشن)")
        
    msg = "\n".join(lines)
    
    try:
        notifier.send_message(msg)
        print("[Report] Sent to Telegram")
    except Exception as e:
        print(f"[Report] Failed to send: {e}")
        print("[Report] Will retry next cycle.")

if __name__ == "__main__":
    main()