\# Phoenix Genesis — Roadmap (Post Phase 1)



وضعیت فعلی: Phase 1 کامل (trailing/BE/partial TP) + real-time dispatch

تاریخ: 2026-10-21

Tag پایه: v0.2.1-dispatch-verified



\---



\## 🔴 فوری (این هفته)



\### 1. تست اهرم ثابت

\- \[ ] 5x Maker (TP=0.4%, SL=0.2%) — در حال اجرا

\- \[ ] 10x Maker (TP=0.2%, SL=0.1%)

\- \[ ] 10x Taker (مقایسه، انتظار زیان)

\- هدف: تأیید مکانیزم + جمع‌آوری ۱۰-۲۰ trade



\### 2. تحلیل confidence

\- \[ ] اجرای analyze\_confidence.py (بعد از ۳۰+ trade)

\- \[ ] آزمون: آیا confidence پیش‌بین سود است؟

\- تصمیم: اگر win rate با confidence صعودی → dynamic leverage



\### 3. رفع باگ archive

\- \[ ] `WARNING: archive save failed: name 'position' is not defined`

\- نیاز: traceback کامل از `\_build\_session\_record`

\- احتمال: `position` بدون `paper\_session.get\_position()` در `main.py`



\---



\## 🟡 Phase 2 — بهینه‌سازی (این ماه)



\### 4. Maker Orders (LIMIT)

\- \[ ] paper\_execution\_engine.py → LIMIT به‌جای MARKET

\- \[ ] شبیه‌سازی fill (اگر قیمت از limit رد شد)

\- اثر: کارمزد 0.12% → 0.04% (۳× کمتر)

\- نیاز: تست ۱۰۰+ trade قبل/بعد



\### 5. ATR-based Position Sizing ⭐ (بهترین انتخاب)

\- \[ ] محاسبه ATR(14) در trend\_filter.py

\- \[ ] SL = 1.5 × ATR, TP = 3.0 × ATR (نسبت ۱:۲)

\- \[ ] quantity = (balance × risk\_pct) / sl\_distance

\- \[ ] risk\_pct = 0.005 (0.5% per trade)

\- اثر: ریسک ثابت، اهرم خودکار، تطبیق با نوسان بازار

\- \*\*توصیه: این بهتر از dynamic leverage است\*\* (۹۰٪ ربات‌های حرفه‌ای)



\### 6. Session Filter

\- \[ ] فقط در ساعات پرحجم: 07:00-10:00 UTC (London) + 13:00-16:00 UTC (NY)

\- \[ ] در ساعات مرده (22:00-04:00 UTC) معامله نکن

\- اثر: کاهش spread و slippage



\### 7. Volatility Filter

\- \[ ] ATR(14) < 0.5% → no trade (بازار مرده)

\- \[ ] ATR(14) > 3% → no trade (بازار دیوانه)

\- \[ ] فقط 0.5-3% معامله کن

\- اثر: حذف ۴۰-۶۰٪ معاملات بی‌کیفیت



\### 8. News Filter

\- \[ ] قبل/بعد CPI, FOMC, NFP → ۳۰ دقیقه توقف

\- منبع: economic calendar API (مثلاً Investing.com)

\- اثر: اجتناب از گپ‌های خبری

### 8.5. Chart Patterns (فیلتر کمکی) 🟡
- [ ] نصب کتابخانه: `pip install motosan-ta-sdk` یا `trendlib`
- [ ] ساخت `intelligence/pattern_detector.py`:
      - ورودی: لیست کندل (30m یا 4H)
      - خروجی: {"pattern": "cup_handle", "direction": "bullish",
                "confidence": 0.75, "breakout_level": 85000}
- [ ] الگوهای هدف (اولویت): cup_handle، double_bottom، double_top،
      head_shoulders
- [ ] اتصال به `DecisionEngine.decide()` به‌صورت **فیلتر** (نه جایگزین):
      - اگر pattern مخالف سیگنال فعلی → BLOCK ورود
      - اگر هم‌جهت → +5 تا +10 به confidence (اختیاری)
- ⚠️ خطرها:
      - تشخیص ذهنی → نیاز به قوانین کمّی سخت‌گیرانه
      - نیاز به 100+ کندل تاریخی برای الگوهای بزرگ
      - خطر over-trading در بازار رِنج
- داده مورد نیاز: 250 کندل (که الان داریم ✅)
- تصمیم: فقط بعد از 100+ trade پایه و تحلیل PF

### 8.6. TakeProfit.com API (منبع داده باکیفیت) 🟢
- [ ] مطالعهٔ مستندات: Platform API (All-In plan required)
- [ ] تصمیم: آیا نیاز به دادهٔ فوت‌پرینت/اوردربوک داریم؟
- [ ] فاز 1 (اولویت اول): جایگزینی/تکمیل منبع کندل:
      - افزودن `exchanges/takeprofit_source.py`
      - ثبت در `MarketDataSourceManager`
      - مقایسه کیفیت با XT (دقت قیمت، نبود گپ، speed)
- [ ] فاز 2 (بک‌تست): استفاده از تاریخچه برای Walk-Forward
- [ ] فاز 3 (پیشرفته): CVD، Footprint، TPO Profiles برای تحلیل
      قدرت خریدار/فروشنده
- ⚠️ محدودیت‌ها:
      - Algo Trading: هنوز "SOON" (اجرای معامله ندارد)
      - نیاز به اشتراک All-In (هزینه)
      - ما paper trading هستیم → فعلاً فقط داده کافی است
- تصمیم: اگر داده XT کافی نبود (گپ، latency، دقت) → اولویت بالا
      اگر XT کافی بود → فقط برای Walk-Forward later


\---



\## 🟢 Phase 3 — پیشرفته (۳ ماه)



\### 9. Mean Reversion Strategy (استراتژی دوم)

\- \[ ] RSI < 30 + BB lower + روند 4H صعودی → BUY

\- \[ ] RSI > 70 + BB upper + روند 4H نزولی → SELL

\- هدف: پوشش بازار ranging (۷۰٪ مواقع)

\- نیاز: backtest جداگانه قبل از ادغام



\### 10. Regime Router

\- \[ ] ADX > 25 → trend-following (فعلی)

\- \[ ] ADX < 20 → mean-reversion (جدید)

\- \[ ] 20-25 → no trade

\- اثر: استراتژی خودش را با بازار تطبیق می‌دهد



\### 11. Breakout Strategy (استراتژی سوم)

\- \[ ] قیمت 20 کندل اخیر را رد کرد + volume > 1.5× میانگین

\- \[ ] Donchian channel

\- هدف: گرفتن حرکات بزرگ بعد از فشردگی



\### 12. Dynamic Leverage (فقط اگر confidence پیش‌بین بود)

\- \[ ] LEVERAGE\_TIERS = {

&#x20;      "high":   {"min\_conf": 75, "leverage": 5},

&#x20;      "medium": {"min\_conf": 60, "leverage": 3},

&#x20;      "low":    {"min\_conf": 0,  "leverage": 1}

&#x20;    }

\- \[ ] LEVERAGE\_MAX = 5 (hard cap)

\- \[ ] \*\*risk-per-trade ثابت\*\*: sl\_pct = risk / leverage

\- ⚠️ خطر: Martingale معکوس اگر confidence معکوس باشد

\- \*\*اول ATR-based (#5)، بعد این اگر لازم بود\*\*



\### 13. Confidence Calibration

\- \[ ] Platt scaling یا Isotonic Regression روی ۱۰۰+ trade

\- \[ ] confidence 80 → واقعاً ۸۰٪ برد

\- نیاز: اسکریپت calibration.py



\---



\## 🔵 Phase 4 — Hardening (۳-۶ ماه)



\### 14. Kill Switch

\- \[ ] ۳ ضرر متوالی → توقف ۱ ساعت

\- \[ ] -5% drawdown → توقف کل روز

\- \[ ] anomaly detection (10× سرعت معاملات)



\### 15. Dashboard

\- \[ ] نمودارهای روزانه/هفتگی

\- \[ ] Sharpe ratio, Sortino, Calmar

\- \[ ] مقایسه session ها



\### 16. Daily Report

\- \[ ] خلاصه در تلگرام هر شب ۲۳:۵۹

\- \[ ] PnL روز، win rate، max drawdown



\### 17. Walk-Forward Backtest

\- \[ ] 6 ماه داده تاریخی

\- \[ ] In-sample: Jan-Apr, Out-of-sample: May-Jun

\- \[ ] فقط اگر out-of-sample سودده بود → اجرا



\---



\## ⚠️ قوانین طلایی (نباید فراموش شوند)



1\. \*\*حداقل ۱۰۰+ trade قبل از هر تصمیم استراتژیک\*\*

2\. \*\*حداقل ۳۰ trade per confidence bucket\*\* (برای تحلیل confidence)

3\. \*\*هر تغییر = commit جدا + tag\*\* (قابلیت بازگشت ۵ ثانیه‌ای)

4\. \*\*هیچ‌وقت دو `main.py` هم‌زمان\*\* (race condition)

5\. \*\*هیچ‌وقت `state.json` را وقتی پوزیشن باز است پاک نکن\*\*

6\. \*\*هیچ‌وقت `git reset --hard` وقتی تست در حال اجراست\*\*

7\. \*\*TP/SL کمتر از ۲× کارمزد نگذار\*\* (Maker: 0.04% → TP≥0.1%)

8\. \*\*اهرم بالا = ریسک لیکویید در گپ‌های خبری\*\*




\---



\## 📊 معیارهای پذیرش (Definition of Done)



| فاز | معیار |

|---|---|

| Phase 1 | ✅ Tag v0.2.1 |

| Phase 2 | PF ≥ 1.2 در ۱۰۰ trade، MaxDD < 15% |

| Phase 3 | PF ≥ 1.5 در ۳۰۰ trade، MaxDD < 10% |

| Phase 4 | Sharpe > 1.5، walk-forward consistent |



\---



\## 🔗 مراجع



\- Tag پایه: `v0.2.1-dispatch-verified`

\- Branch: `experiment/scalp-single-strategy`

\- Remote: `github.com/mehdinaderi1/phoenix\_Genesis`

\- مستندات کلیدی: `metrics.py`, `analyze\_5x.py`, `analyze\_confidence.py`

