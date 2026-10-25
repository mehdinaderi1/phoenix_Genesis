# Phoenix Genesis — Session State

**Date:** 2026-10-25
**Branch:** experiment/scalp-single-strategy
**Remote:** https://github.com/mehdinaderi1/phoenix_Genesis.git
**Python:** 3.14

## ✅ Completed (verified end-to-end)

### env-first patches

**execution/paper_position.py**
- Helpers _cfg_bool (L18), _cfg_float (L26) — support both KEY and PHOENIX_KEY
- 7 knobs env-first (L87–116):
  - PARTIAL_TP_ENABLED, PARTIAL_TP_AT_R (×2), PARTIAL_TP_FRACTION
  - BE_ENABLED, TRAILING_ENABLED, TRAILING_START_R, TRAILING_DISTANCE_R
- py_compile: OK

**execution/paper_position_lifecycle.py**
- Imports _cfg_bool, _cfg_float from paper_position
- L54: _cfg_bool("PARTIAL_TP_ENABLED", False)
- L55–56: _cfg_float("TP_EXTEND_AFTER_PARTIAL_R", 3.0)
- py_compile: OK

**End-to-end test (PASSED):**
- PARTIAL fraction env=0.25 -> 0.25
- BE SL env AT_R=0.1 -> 80000
- TRAILING SL env start=0.5 dist=0.2 -> 79960.0

### Git
- .gitignore tightened: *.bak.*, *_apply_*.py, env.local.ps1, runtime data
- Commits: 56d6fb8 (patches), 5c5e535 (gitignore)
- Push OK to origin/experiment/scalp-single-strategy

## 🎯 Trend Rider identified

- **Trend Rider = BTCMTFTrendAlignmentV1** in intelligence/trading_strategy.py
  - 
ame = "BTC_MTF_TREND_ALIGNMENT_V1"
  - Multi-TF: 5m primary, 15m/30m/1H context, 4H higher
  - Already env-first: PHOENIX_RELAXED_ALIGNMENT, PHOENIX_VETO_ALIGNMENT
- **Entrypoint:** python .\main.py (NOT python -m trend_rider)
- main() at line 393

## 🧪 Live test run (2026-10-25 11:29)

- Command: python .\main.py
- Result: SUCCESS — 20 cycles, 0 errors, 1 position opened
- Strategy: BTC_MTF_TREND_ALIGNMENT_V1 every cycle
- Position: SELL @ 80667.65 | SL=80748.32 | TP=80506.31 (2R ratio)
- Result: OPEN: 1, HOLD: 19, CLOSE: 0, Balance: 1000.0, PnL: 0.0
- No PARTIAL/SL_MOVE/TP_EXTEND triggered in live (price moved only ~0.02R)
- Log: un_trend_rider.log
- Archive: data/paper_sessions/<session-id>

## ⚠️ Known issues / gotchas

1. **PowerShell Execution Policy blocks .ps1 files**
   - Fix: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass (per-session only)
2. **PARTIAL_TP_AT_R is shared between Partial trigger AND BE trigger**
   - Changing one changes both. Undocumented coupling.
3. **config/settings.py has TWO class Settings: blocks** — first is dead code
4. **TP_EXTEND_AFTER_PARTIAL_R consumed in paper_position_lifecycle.py**, not in paper_position.py
5. **Leverage discrepancy:** Settings.LEVERAGE=1 but log shows Lev=20x — set elsewhere

## 🔧 env.local.ps1 (gitignored, recreate on each device)

    \true          = "true"
    \1.5          = "1.5"
    \0.3       = "0.3"
    \true                = "true"
    \true        = "true"
    \1.0           = "1.0"
    \0.5       = "0.5"
    \10 = "10"

Load in PowerShell:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    . .\env.local.ps1
    python .\main.py

## 🔍 Verify patches in log

    Select-String .\run_trend_rider.log -Pattern "PARTIAL|SL_MOVE|TP_EXTEND|Strategy="

## 📦 Backups (gitignored, on disk only)

- execution/paper_position.py.bak.20261025_104000
- execution/paper_position_lifecycle.py.bak.20261025_104716
- config/settings.py.bak.20261025_104000

## 🚀 Resume on second device

    cd C:\Users\<user>\Desktop
    git clone https://github.com/mehdinaderi1/phoenix_Genesis.git
    cd phoenix_Genesis
    git checkout experiment/scalp-single-strategy
    Get-Content .\STATE.md
    # recreate env.local.ps1 from above
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    . .\env.local.ps1
    python .\main.py

## 🎯 TODO

- [ ] Verify env-first PARTIAL/SL_MOVE/TP_EXTEND in live run (need price move >1R)
- [ ] Decouple BE threshold from PARTIAL_TP_AT_R (add BE_AT_R setting)
- [ ] Investigate leverage 20x vs Settings.LEVERAGE=1
- [ ] Remove duplicate class Settings in config/settings.py
- [ ] Merge experiment branch -> master when stable
