# Context Capsule — 2026-10-30

## پروژه
phoenix_Genesis — ربات فیوچرز XT (DRY RUN)

## وضعیت فعلی
- WireSock Secure Connect + MTU=1280 + split-tunnel (python, PowerShell, VS Code, مرورگر tunneled)
- Runner: ۳ fix BTC fetch + MTU → پایدار
- Watcher: سالم
- پوزیشن‌های دستی: BTC SHORT 121 @ 76599.1 | ETH SHORT 16 @ 2262.18 ([LOCK]، Runner دست نمی‌زند)
- بازار: ریزش شدید، ۲۳ ارز زیر کف ۴H، BTC=FLAT
- ZEC تنها survivor (POS% +34.8%)

## ابزارهای ساخته‌شده
- tools/diag_channels.py — تشخیص موقعیت در کانال
- tools/break_retest_detector.py — دو الگو (BD/BO) + watchlist
  - Channel: 4H Donchian(30) | Trigger: 1H closed
  - BREAK_WINDOW=12, MIN_BREAK_AGE=2, MIN_RR=1.0

## وضعیت آخر (۲۲ ارز FRESH BREAK)
- نزدیک‌ترین: DOGE (POS% -5.1, break_too_fresh 1<2)
- صفر hit — منتظر retest واقعی

## قدم بعدی
1. صبح: git push (VPN قطع)
2. اجرای break_retest_detector.py --verbose
3. اگر hit پیدا شد → بررسی R:R + SL/TP قبل از هر اقدام
4. اگر همچنان FRESH BREAK → صبر
5. تصمیم دربارهٔ ادغام detector در Runner با flag XT_RUNNER_BR_ENABLED=1

## دستورهای اجرا (بعد از بیدار شدن)
```powershell
. .\env.local.ps1
$env:XT_RUNNER_MAX_POS = "2"
$env:XT_RUNNER_TIMEOUT_HOURS = "4"
$env:XT_RUNNER_MAX_CYCLES = "0"
$env:XT_RUNNER_INTERVAL = "60"
python tools\futures_strategy_runner.py     # ترمینال ۱

python tools\watch_state.py                  # ترمینال ۲

python tools\break_retest_detector.py --verbose   # ترمینال ۳ (هر ۱ ساعت)
