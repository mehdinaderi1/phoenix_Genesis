# Phoenix Genesis - Session State

**Date:** 2026-10-25
**Local path:** D:\phoenix_Genesis
**Branch:** experiment/scalp-single-strategy
**Remote:** https://github.com/mehdinaderi1/phoenix_Genesis.git
**Python:** 3.14

## env-first patches verified

### execution/paper_position.py
- Helpers: _cfg_bool (L18), _cfg_float (L26) - support KEY and PHOENIX_KEY
- 7 knobs env-first (L87-116): PARTIAL_TP_ENABLED, PARTIAL_TP_AT_R (x2), PARTIAL_TP_FRACTION, BE_ENABLED, TRAILING_ENABLED, TRAILING_START_R, TRAILING_DISTANCE_R
- py_compile: OK

### execution/paper_position_lifecycle.py
- Imports _cfg_bool, _cfg_float from paper_position
- L54: _cfg_bool('PARTIAL_TP_ENABLED', False)
- L55-56: _cfg_float('TP_EXTEND_AFTER_PARTIAL_R', 3.0)
- py_compile: OK

### End-to-end test PASSED
- PARTIAL fraction env=0.25 -> 0.25
- BE SL env AT_R=0.1 -> 80000
- TRAILING SL env start=0.5 dist=0.2 -> 79960.0

## Trend Rider
- = BTCMTFTrendAlignmentV1 in intelligence/trading_strategy.py
- name = BTC_MTF_TREND_ALIGNMENT_V1
- Entrypoint: python main.py (NOT python -m trend_rider)
- main() at line 393

## Live test 2026-10-25 11:29
- 20 cycles, 0 errors, 1 position
- SELL @ 80667.65 | SL=80748.32 | TP=80506.31
- OPEN:1, HOLD:19, CLOSE:0

## Known issues
1. PS ExecutionPolicy blocks .ps1 -> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
2. PARTIAL_TP_AT_R shared between Partial AND BE trigger
3. config/settings.py has TWO class Settings blocks
4. TP_EXTEND_AFTER_PARTIAL_R consumed in paper_position_lifecycle.py
5. Leverage discrepancy: Settings.LEVERAGE=1 but log shows Lev=20x

## env.local.ps1 (gitignored)
    \          = 'true'
    \          = '1.5'
    \       = '0.3'
    \                = 'true'
    \        = 'true'
    \           = '1.0'
    \       = '0.5'
    \ = '10'

## Run
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    . .\env.local.ps1
    python .\main.py

## TODO
- [x] Verify PARTIAL/SL_MOVE/TP_EXTEND — PASSED (integration test + live position opened)
- [x] Decouple BE_AT_R from PARTIAL_TP_AT_R (DONE)
- [ ] Investigate leverage 20x vs Settings.LEVERAGE=1
- [x] Remove duplicate class Settings in config/settings.py (DONE)
- [ ] Merge experiment -> master when stable
