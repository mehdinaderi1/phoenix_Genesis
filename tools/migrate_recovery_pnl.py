"""
Migration: 4 سشن قدیمی pre-patch که PnL recovery در cycles[] نداشتند.
- delta = summary.total_pnl - sum(cycles.realized_pnl)
- اگر |delta| > 1e-6: یک cycle مصنوعی اضافه می‌کند
- قبل از هر تغییر، بکاپ .bak می‌گیرد
- فایل را atomic بازنویسی می‌کند

Usage:
  python tools/migrate_recovery_pnl.py --dry-run
  python tools/migrate_recovery_pnl.py
"""
import json, sys, shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("data/paper_sessions")

# فقط sessionهایی که pre-patch هستند و delta دارند
TARGETS = [
    "9cc43947-2238-4b81-b14f-1d4411352e4e",
    "c8d5f3e7-a83c-4f0c-a30e-e36f97f64bc0",
    "1b1bd06b-9c91-478d-b453-8b251fd557d6",
    "6cdd881f-b925-4c03-a869-ccb40a13edf7",
]


def migrate_one(path: Path, dry_run: bool) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    summary = data.get("summary") or {}
    cycles = data.get("cycles") or []

    sum_realized = sum((c.get("realized_pnl") or 0.0) for c in cycles)
    total_pnl = summary.get("total_pnl", 0.0)
    delta = total_pnl - sum_realized

    result = {
        "session": path.stem,
        "before_cycles": len(cycles),
        "before_delta": delta,
        "action": "noop",
    }

    if abs(delta) < 1e-6:
        result["action"] = "already_reconciled"
        return result

    # cycle مصنوعی
    synthetic = {
        "cycle": 0,
        "symbol": "BTCUSDT",
        "price": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_status": None,
        "fallback_used": None,
        "consensus_breakdown": None,
        "signal": None,
        "trend": None,
        "regime": None,
        "confidence": None,
        "risk": None,
        "proposal_action": None,
        "proposal_status": None,
        "proposal_reason": None,
        "action": "RECOVERY_CLOSE",
        "execution_status": "CLOSED",
        "realized_pnl": delta,
        "position_side": None,
        "entry_price": None,
        "quantity": None,
        "leverage": 1.0,
        "opportunity": None,
        "opportunity_observation_error": None,
        "error": None,
        "_migration_note": "backfilled by migrate_recovery_pnl.py",
    }

    cycles_new = cycles + [synthetic]
    sum_new = sum_realized + delta

    summary = dict(summary)
    summary["pnl_reconcile_delta"] = 0.0
    summary["pnl_reconciled"] = True
    summary["cycles_processed"] = len(cycles_new)
    summary["_migration_note"] = (
        f"added recovery cycle with realized_pnl={delta:.10f}"
    )

    data["cycles"] = cycles_new
    data["summary"] = summary

    result["after_cycles"] = len(cycles_new)
    result["after_delta"] = total_pnl - sum_new
    result["action"] = "migrated"

    if not dry_run:
        # backup
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)

        # atomic write
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        tmp.replace(path)

    return result


def main():
    dry_run = "--dry-run" in sys.argv

    print(f"{'session':36} {'before':>7} {'delta_before':>14} "
          f"{'action':>18} {'delta_after':>14}")
    print("-" * 100)

    for sid in TARGETS:
        path = ROOT / f"{sid}.json"
        if not path.exists():
            print(f"{sid:36} MISSING")
            continue
        try:
            r = migrate_one(path, dry_run)
        except Exception as e:
            print(f"{sid:36} ERROR: {e}")
            continue
        print(f"{r['session']:36} {r['before_cycles']:>7} "
              f"{r['before_delta']:>+14.6f} {r['action']:>18} "
              f"{r.get('after_delta', 0):>+14.6f}")

    if dry_run:
        print("\n[DRY-RUN] هیچ فایلی تغییر نکرد. برای اجرا: بدون --dry-run")
    else:
        print("\n✓ Migration انجام شد. بکاپ‌ها با پسوند .bak ذخیره شدند.")


if __name__ == "__main__":
    main()
